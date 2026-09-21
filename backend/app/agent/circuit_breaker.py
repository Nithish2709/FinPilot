import enum
import time
from typing import Optional


class CircuitState(str, enum.Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """
    In-memory stateful circuit breaker for primary local LLM.
    CLOSED: Normal local requests.
    OPEN: Primary has failed repeatedly; requests temporarily route to fallback.
    HALF_OPEN: Cooldown expired; allows a single canary request to test recovery.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        cooldown_seconds: float = 30.0,
    ):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_failure_time: Optional[float] = None

    def can_attempt_local(self) -> bool:
        """Determines if the local primary provider can be attempted."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            now = time.time()
            if self.last_failure_time and (now - self.last_failure_time) >= self.cooldown_seconds:
                # Transition to HALF_OPEN to test canary request
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            return True

        return True

    def record_success(self) -> None:
        """Records a successful response, resetting circuit to CLOSED."""
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_failure_time = None

    def record_failure(self) -> None:
        """Records a failure and trips to OPEN if threshold is reached."""
        self.consecutive_failures += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # Canary test failed; immediately trip back to OPEN
            self.state = CircuitState.OPEN
        elif self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

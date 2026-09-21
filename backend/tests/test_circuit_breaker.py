import time
import pytest
from app.agent.circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_breaker_initial_state_closed():
    cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=0.1)
    assert cb.state == CircuitState.CLOSED
    assert cb.can_attempt_local() is True


def test_circuit_breaker_trips_to_open():
    cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=0.1)
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    cb.record_failure()
    # Tripped after 3 consecutive failures
    assert cb.state == CircuitState.OPEN
    assert cb.can_attempt_local() is False


def test_circuit_breaker_cooldown_and_recovery():
    cb = CircuitBreaker(failure_threshold=2, cooldown_seconds=0.05)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

    # Wait for cooldown to expire
    time.sleep(0.06)
    # Testing can_attempt_local should transition to HALF_OPEN
    assert cb.can_attempt_local() is True
    assert cb.state == CircuitState.HALF_OPEN

    # Success in HALF_OPEN recovers to CLOSED
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.consecutive_failures == 0


def test_circuit_breaker_half_open_failure_reopens():
    cb = CircuitBreaker(failure_threshold=2, cooldown_seconds=0.05)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

    time.sleep(0.06)
    assert cb.can_attempt_local() is True
    assert cb.state == CircuitState.HALF_OPEN

    # Failure during canary re-opens circuit immediately
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

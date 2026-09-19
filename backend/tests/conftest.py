import asyncio
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# In-memory SQLite database for isolated unit testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    """Sets up fresh in-memory database tables for each test."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _create_tables() -> None:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    loop.run_until_complete(_create_tables())
    yield
    loop.close()


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency override for test database sessions."""
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client() -> TestClient:
    """Fixture providing FastAPI TestClient."""
    with TestClient(app) as test_client:
        yield test_client

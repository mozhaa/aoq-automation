from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
    AsyncEngine,
)
from aoq_automation.config import config
from .models import Base

engine: AsyncEngine
async_session: async_sessionmaker[AsyncSession]


def get_database_url() -> str:
    if config["database"]["database"] == "postgres":
        return URL.create(
            drivername="postgresql+asyncpg",
            **config["database.postgres"],
        )
    elif config["database"]["database"] == "sqlite3":
        return f"sqlite+aiosqlite:///{config["database.sqlite3"]["file"]}"
    else:
        raise RuntimeError(f"Database {config["database"]} is not supported")


def connection(func):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)

    return wrapper


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def connect() -> None:
    global engine, async_session
    engine = create_async_engine(url=get_database_url())
    async_session = async_sessionmaker(engine, class_=AsyncSession)

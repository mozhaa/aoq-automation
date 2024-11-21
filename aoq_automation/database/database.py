from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from aoq_automation.config import config

from .models import Base


class Database:
    def _get_database_url() -> str:
        if config["database"]["database"] == "postgres":
            return URL.create(
                drivername="postgresql+asyncpg",
                **config["database.postgres"],
            )
        elif config["database"]["database"] == "sqlite3":
            return f"sqlite+aiosqlite:///{config["database.sqlite3"]["file"]}"
        else:
            raise RuntimeError(f"Database {config["database"]} is not supported")

    def connect(self, echo: bool = False) -> None:
        self._engine = create_async_engine(url=Database._get_database_url(), echo=echo)
        self._async_session = async_sessionmaker(self._engine, class_=AsyncSession)

    async def create_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def async_session(self, **kwargs) -> AsyncSession:
        return self._async_session(**kwargs)


db = Database()

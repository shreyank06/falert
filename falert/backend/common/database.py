from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def create_engine() -> AsyncEngine:
    return create_async_engine(
        "postgresql+asyncpg://falert:falert@127.0.0.1/falert",
        echo=True,
    )


from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from shared.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def init_db():
    """Initialize database tables safely.

    MySQL advisory lock prevents multiple microservices from
    creating the same tables concurrently during startup.
    """
    from shared.models import Base as ModelsBase

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "SELECT GET_LOCK('video_platform_schema_init', 60)"
        )

        try:
            ModelsBase.metadata.create_all(bind=connection)
        finally:
            connection.exec_driver_sql(
                "SELECT RELEASE_LOCK('video_platform_schema_init')"
            )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import logging
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

logger = logging.getLogger(__name__)


def engine_factory() -> Engine:
    database_url = "postgresql://trace_admin:trace_admin@localhost/trace"
    engine = create_engine(database_url)
    logger.debug(f"SQLALchemy engine loaded. url={database_url} db=trace")
    return engine


def session_factory() -> Session:
    s = scoped_session(
        sessionmaker(bind=engine_factory(), autocommit=False, autoflush=False)
    )
    logger.debug("SQLAlchemy session loaded.")
    return s


def get_db():
    db = session_factory()()
    try:
        yield db
    finally:
        db.close()

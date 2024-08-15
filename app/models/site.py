from uuid6 import uuid7

from sqlalchemy import Column, String, select, Float
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


class Site(Base):
    """Site is the overarching model of a url within trace,
    and will save all relevent information; such as avg time,
    test results, logos, and a nickname
    """

    __tablename__ = "sites"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    name = Column(String(), nullable=False)
    url = Column(String(), nullable=False)
    img = Column(String())
    status = Column(String())
    avg_time = Column(Float())

    # relationships
    # TODO: results = relationship(pingresult)

    # these methods could (and should imo) easily be genericized to a base class
    # but this will do for now with how small this project is
    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        transaction = cls(**kwargs)
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction

    @classmethod
    async def get(cls, db: AsyncSession, id: str):
        try:
            transaction = await db.get(cls, id)
        except NoResultFound:
            return None
        return transaction

    @classmethod
    async def get_all(cls, db: AsyncSession):
        # odd way to do this perhaps?
        # i think a better SQA 2.0 syntax would be
        # TODO: db.get(cls).all()
        return (await db.execute(select(cls))).scalars().all()

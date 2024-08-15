from sqlalchemy import Column, String, select, Float, ForeignKey
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class SiteToResult(Base):
    """Site to Result linking table"""

    __tablename__ = "site_to_result"

    # fks
    site_id = Column(
        UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), primary_key=True
    )
    result_id = Column(
        UUID(as_uuid=True),
        ForeignKey("results.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # relationships
    site = relationship("Site", back_populates="result_associations")
    result = relationship("Result", back_populates="site_associations")

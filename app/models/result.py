from uuid6 import uuid7

from sqlalchemy import Column, Float
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base
from app import models


class Result(Base):
    """Result is a simple model to store an individual tcptraceroute hop result"""

    __tablename__ = "results"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    time = Column(Float())

    # Site to REsult relationship
    site_associations = relationship(
        "SiteToResult", back_populates="result", cascade="all, delete-orphan"
    )
    site = association_proxy(
        "site_associations", "site", creator=lambda site: models.SiteToResult(site=site)
    )

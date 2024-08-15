import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel, HttpUrl, IPvAnyAddress
from app.models.site import Site as SiteModel
from app.db import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
import re

import subprocess

router = APIRouter()


class PingResult(BaseModel):
    time: float


class SiteBaseSchema(BaseModel):
    name: str
    url: HttpUrl | IPvAnyAddress
    img: HttpUrl | None = None


class SiteFullSchema(SiteBaseSchema):
    status: str | None = None
    results: list[PingResult] | None = None
    avg_time: float | None = None


class SiteSchema(SiteBaseSchema):
    id: int


@router.post("/create", response_model=SiteFullSchema)
async def create_site(
    site: SiteBaseSchema, db: AsyncSession = Depends(get_db_session)
) -> SiteFullSchema:
    """Creates a new site object and runs an initial test"""
    new_site = await SiteModel.create(db, **site.model_dump)
    results, avg_time = _run_test(new_site)
    new_site.avg_time = avg_time
    # TODO: append results
    await db.commit()

    return new_site


def _run_test(site: SiteModel) -> tuple[list, float]:
    output = subprocess.run(
        f'traceroute "{str(site.url)}"', text=True, shell=True, capture_output=True
    ).stdout.split("\n")

    for hop in reversed(output):
        match = re.findall(r"\d+\.\d+ ms", hop)

        if match:
            break

    results = []
    tot_time: float = 0.0
    for time in match:
        results.append(PingResult(**{"time": time}))
        tot_time += float(re.search(r"\d+.\d+", time).group(0))

    avg_time = tot_time / len(match)

    return (results, avg_time)

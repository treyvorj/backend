import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel, HttpUrl, IPvAnyAddress
from app.models.site import Site as SiteModel
from app.db import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
import re

import subprocess

router = APIRouter()


class Result(BaseModel):
    time: float


class SiteBaseSchema(BaseModel):
    name: str
    url: HttpUrl | IPvAnyAddress | str
    img: HttpUrl | None = None


class SiteFullSchema(SiteBaseSchema):
    id: uuid.UUID
    status: str | None = None
    # results: list[Result] | None = None
    avg_time: float | None = None


class SiteSchema(SiteBaseSchema):
    id: uuid.UUID


# this MUST be above get_site to prevent interpreting 'all' as the id
@router.get("/all", response_model=list[SiteFullSchema])
async def get_sites(db: AsyncSession = Depends(get_db_session)) -> list[SiteFullSchema]:
    """Returns a list of all site objects"""
    sites = await SiteModel.get_all(db)
    return sites


@router.get("/{site_id}", response_model=SiteFullSchema)
async def get_site(
    site_id: uuid.UUID, db: AsyncSession = Depends(get_db_session)
) -> SiteFullSchema:
    """Returns site by ID"""
    site = await SiteModel.get(db, id=site_id)
    return site


@router.post("/{site_id}/run", response_model=SiteFullSchema)
async def run_trace(
    site_id: uuid.UUID, db: AsyncSession = Depends(get_db_session)
) -> SiteFullSchema:
    """Returns site by ID"""
    site = await SiteModel.get(db, id=site_id)
    results = []
    avg_time = None
    try:
        results, avg_time = _run_test(site)
    except Exception as e:
        print(str(e))
        site.status = "FAILURE"

    if len(results) > 0:
        site.status = "SUCCESS"
    else:
        site.status = "NO RESULTS"

    if avg_time:
        site.avg_time = avg_time
    # TODO: append results
    await db.commit()

    return site


@router.post("/create", response_model=SiteFullSchema)
async def create_site(
    site: SiteBaseSchema, db: AsyncSession = Depends(get_db_session)
) -> SiteFullSchema:
    """Creates a new site object and runs an initial test"""
    new_site = await SiteModel.create(db, **site.model_dump())
    results = []
    avg_time = None
    try:
        results, avg_time = _run_test(new_site)
    except Exception as e:
        print(str(e))
        new_site.status = "FAILURE"

    if len(results) > 0:
        new_site.status = "SUCCESS"
    else:
        new_site.status = "NO RESULTS"

    if avg_time:
        new_site.avg_time = avg_time
    # TODO: append results
    await db.commit()

    return new_site


def _run_test(site: SiteModel) -> tuple[list, float | None]:
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
        float_time = float(re.search(r"\d+.\d+", time).group(0))
        results.append(Result(**{"time": float_time}))
        tot_time += float_time

    avg_time = None
    if len(match) > 0:
        avg_time = tot_time / len(match)

    return (results, avg_time)

import uuid
from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl, IPvAnyAddress
import re

import subprocess

router = APIRouter()


class PingResult(BaseModel):
    time: float


class SiteBase(BaseModel):
    id: int
    name: str
    url: HttpUrl | IPvAnyAddress
    img: HttpUrl | None = None


class SiteFull(SiteBase):
    status: str | None = None
    results: list[PingResult] | None = None
    avg_time: float | None = None


@router.post("/")
async def create_site(site: SiteBase) -> SiteFull:
    """Creates a new site object and runs an initial test"""
    response = SiteFull(
        **{"id": site.id, "name": site.name, "url": site.url, "img": site.img}
    )

    output = subprocess.run(
        f'traceroute "{str(site.url)}"', text=True, shell=True, capture_output=True
    ).stdout.split("\n")

    for hop in reversed(output):
        match = re.findall(r"\d+\.\d+ ms", hop)

        if match:
            break

    response.results = []
    tot_time: float = 0.0
    for time in match:
        response.results.append(PingResult(**{"time":time}))
        tot_time += float(re.search(r"\d+.\d+", time).group(0))

    response.avg_time = tot_time / len(match)

    return response

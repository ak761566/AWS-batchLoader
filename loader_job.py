from time import sleep

import requests
import asyncio
import httpx
import time
from typing import Any, Tuple
from dataclasses import dataclass
from collections.abc import Callable
import random

setup_url = "http://awe1ptstpeps01.aws.portico.org:9500/loader/job/multistepjob/v1/submitwithjson/LoaderJob"
innodata_url = "http://awe1ptindeps01.aws.portico.org:9500/loader/job/multistepjob/v1/submitwithjson/LoaderJob"
headers = {"accept":"*/*", "Content-Type": "application/json"}

setup_json_data = {"configSourceType":"GIT", "propertyFileName":"AMD-CARIBNEWS_I-LoaderConfig.properties", "loaderProfileFileName":"AMD-CARIBNEWS_I-LoaderProfile.xml"}
#{"configSourceType":"GIT", "propertyFileName":"INNOVATIVE-Meridian-LoaderConfig.properties", "loaderProfileFileName":"INNOVATIVE-LoaderProfile.xml"}
innodata_json_data = {"configSourceType":"GIT", "propertyFileName":"INNOVATIVE-Meridian-LoaderConfig.properties", "loaderProfileFileName":"INNOVATIVE-LoaderProfile.x"}

setup_job_status = "http://awe1ptstpeps01.aws.portico.org:9500/loader/job/v1/status/"
innoLoader_job_status = f"http://awe1ptindeps01.aws.portico.org:9500/loader/job/v1/status/"

timeout_seconds = 60.0
poll_interval = 1.0


@dataclass(frozen=True)
class JobStatus:
    job_id: str
    job_result: str
    job_status: str
    errors : list[str]

    @property
    def is_terminal(self):
        return self.job_result in {"COMPLETED", "FINISHED"} or bool(self.errors)




async def run_loader(client: httpx.AsyncClient, url: str, header: dict[str, str], json_data : dict[str, Any])->int:
    response = await client.post(url=url, headers=header, json=json_data)
    response.raise_for_status()
    data: dict[str, Any] = response.json()
    if "jobId" not in data:
        raise ValueError(f"Response missing job Id : {data}")
    print(data.get("jobId"))
    return int(data.get("jobId"))


async def fetch_job_status(client: httpx.AsyncClient, url:str, job_id: int, on_log: Callable[[str], None] | None = None)->JobStatus | None:
    try:
        response = await client.get(f"{url}/{job_id}")
        response.raise_for_status()
    except (httpx.TransportError, httpx.HTTPStatusError) as exc:
        if isinstance(exc, httpx.HTTPStatusError) and  exc.response.status_code < 500:
            raise
        if on_log:
            on_log(f"Transient error polling job {job_id} : {exc!r} will retry.")
        return None

    data : dict[str, Any] = response.json()
    return JobStatus(
        job_id = data.get("jobId",""),
        job_result=data.get("jobResult",""),
        job_status=data.get("jobStatus",""),
        errors=data.get("errors",[])
    )


async def wait_for_long_job(client: httpx.AsyncClient, url:str, job_id: int,
                            min_interval: float = 5.0, max_interval:float = 300.0, max_hours=12, on_log: Callable[[str], None] | None = None)->JobStatus:

    deadline = asyncio.get_event_loop().time() + (max_hours * 3600)
    delay = min_interval

    while asyncio.get_event_loop().time() < deadline:
        status = await fetch_job_status(client, url, job_id)

        if status and status.is_terminal:

            if status.errors:
                raise RuntimeError(f"Job {job_id} failed with exc {status.errors}")
                # for error in status.errors:
                #     raise RuntimeError(f"Job {job_id} failed with exc {error}")

            return status
        else:
            if on_log:
                on_log(f"Job {job_id} -> Status {status.job_status or 'N/A'}, result {status.job_result or 'Pending'}")

        jitter = random.uniform(0, delay * 0.1)
        await asyncio.sleep(delay + jitter)
        delay = min(delay*1.5, max_interval)



async def poll_job(loader_endpoint: str, status_endpoint: str, header : dict[str, Any], json_data: dict[str, Any], on_log: Callable[[str], None] | None = None)->JobStatus:
    async with httpx.AsyncClient() as client:
        job_id = await run_loader(client, loader_endpoint, header, json_data)

        if on_log:
            on_log(f"Submitted job successfully, Assigned Job_Id {job_id}")

        status = await wait_for_long_job(client, status_endpoint, job_id, on_log=on_log)
        return status


async def main():
    async with httpx.AsyncClient() as client:
        # job_id = await run_loader(client, setup_url, headers, setup_json_data)
        # status = await wait_for_long_job(client, setup_job_status, job_id)

        job_id = await run_loader(client, innodata_url, headers, innodata_json_data)
        status = await wait_for_long_job(client, innoLoader_job_status, job_id)
        print(status)


if __name__ == "__main__":
    asyncio.run(main())
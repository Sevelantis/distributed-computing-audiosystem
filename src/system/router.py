from http import HTTPStatus
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from src.dependencies import system_service

from src.system.job.schema import JobStatsCreate, JobStatsRead
from src.system.schema import ResetRead
from src.system.service import SystemService

system_router = APIRouter()

@system_router.get(
    '/job',
    response_model=list[int]
    )
def list_all_jobs(
    system_service: SystemService = Depends(system_service),
    ) -> JSONResponse:
    
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=system_service.list_all_jobs()
    )

@system_router.get(
    '/job/{job_id}',
    response_model=JobStatsRead,
    responses={HTTPStatus.NOT_FOUND: {'description': 'Job not found.'}}
    )
def job_stats(
    schema: JobStatsCreate = Depends(JobStatsCreate),
    system_service: SystemService = Depends(system_service),
    ) -> JSONResponse:
    try:
        
        return JSONResponse(
            status_code=HTTPStatus.OK,
            content=json.loads(system_service.job_stats(schema=schema).json())
        )
    except HTTPException as e:
        if e.status_code == HTTPStatus.NOT_FOUND:
            
            return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content='Job not found.'
            )

@system_router.post(
    '/reset',
    response_model=ResetRead
    )
def reset(
    system_service: SystemService = Depends(system_service),
    ) -> JSONResponse:
    try:
        system_service.reset()
    
        return JSONResponse(
            status_code=HTTPStatus.OK,
            content='Ok.'
        )
    except Exception as e:

        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content='Failed to reset.'
        )

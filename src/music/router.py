import json
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from src.dependencies import music_service
from src.music.service import MusicService
from src.music.schema import MusicProcessCreate, MusicProcessRead, MusicProgressCreate, MusicProgressRead, MusicSubmitCreate, MusicSubmitRead
from fastapi.responses import FileResponse


music_router = APIRouter()

@music_router.get(
    '/music',
    response_model=list[MusicSubmitRead],
    )
def list_all(
    music_service: MusicService = Depends(music_service)
    ) -> JSONResponse:
    
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=[ json.loads(music.json()) for music in music_service.list_all() ]
    )

@music_router.post(
    '/music/{music_id}',
    response_model=MusicProcessRead,
    responses={
        HTTPStatus.NOT_FOUND: {'description': 'Music not found.'},
        HTTPStatus.METHOD_NOT_ALLOWED: {'description': 'Track not found.'}
        }
    )
def process(
    schema: MusicProcessCreate = Depends(MusicProcessCreate),
    music_service: MusicService = Depends(music_service)
    ) -> JSONResponse:
    try: 
        
        return JSONResponse(
            status_code=HTTPStatus.OK,
            content=json.loads(music_service.process(schema=schema).json())
        )
    except HTTPException as e:
        if e.status_code == HTTPStatus.NOT_FOUND:
            
            return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content="Music not found."
            )
        elif e.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
            
            return JSONResponse(
                status_code=HTTPStatus.METHOD_NOT_ALLOWED,
                content="Track not found."
            )
        
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content="Ok."
        )

@music_router.get(
    '/music/{music_id}',
    response_model=MusicProgressRead,
    responses={HTTPStatus.NOT_FOUND: {'description': 'Music not found.'},}
    )
def progress(
    schema: MusicProgressCreate = Depends(MusicProgressCreate),
    music_service: MusicService = Depends(music_service)
    ) -> JSONResponse:
    try:
        
        return JSONResponse(
            status_code=HTTPStatus.OK,
            content=json.loads(music_service.progress(schema=schema).json())
            )
    except HTTPException as e:
        if e.status_code == HTTPStatus.NOT_FOUND:
            
            return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content='Music not found.'
            )

@music_router.post(
    '/music',
    response_model=MusicSubmitRead,
    responses={HTTPStatus.METHOD_NOT_ALLOWED: {'description': 'Invalid input.'},}
    )
def submit(
    schema: MusicSubmitCreate = Depends(MusicSubmitCreate),
    music_service: MusicService = Depends(music_service)
    ) -> JSONResponse:
    try:

        return JSONResponse(
            status_code=HTTPStatus.OK,
            content=json.loads(music_service.submit(schema=schema).json())
            )
    except HTTPException as e:
        if e.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
            
            return JSONResponse(
                status_code=HTTPStatus.METHOD_NOT_ALLOWED,
                content="Invalid input."
            )

@music_router.get('/mp3/{uri:path}')
async def get_mp3(uri: str):
    import os
    if not os.path.exists(path=uri):
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content=f'File: {uri} does not exist.'
        )
    return FileResponse(
        status_code=HTTPStatus.OK,
        media_type='audio/mpeg',
        path=uri
    )


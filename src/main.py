'''main.py is a root of the project, which inits the FastAPI app'''

import logging

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import src.config as config
from src.dependencies import server_worker_manager
from src.music.router import music_router
from src.system.router import system_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger('stomp').setLevel(logging.ERROR)
logging.getLogger('uvicorn').setLevel(logging.ERROR)


app = FastAPI(openapi_url="/api/v1/openapi.yaml")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[str(origin) for origin in config.BACKEND_CORS_ORIGINS],
    allow_methods=["*"],
    allow_headers=["*"],
    )


@app.on_event("startup")
def startup_event() -> None:
    logging.info('Server startup.')
    
    from src.dependencies import storage
    storage().reset()
    server_worker_manager().submit_threadpool()
    
@app.on_event("shutdown")
def shutdown_event() -> None:
    logging.info('Server shutdown.')
    server_worker_manager().stop_threadpool()

app.include_router(router=music_router)
app.include_router(router=system_router)

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host=config.APP_HOST,
        port=int(config.APP_PORT),
        log_level=logging.ERROR
    )

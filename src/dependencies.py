

from fastapi import Depends

from src.broker.dispatcher import Dispatcher
from src.music.factory import MusicFactory
from src.music.repository import MusicRepository
from src.music.service import MusicService
from src.storage.storage import Storage
from src.system.job.factory import JobFactory
from src.system.job.repository import JobRepository
from src.system.service import SystemService
from src.utils import IdManager

id_manager_instance = IdManager()
def id_manager() -> IdManager:
    
    return id_manager_instance


music_repository_instance = MusicRepository()
def music_repository() -> MusicRepository:
    
    return music_repository_instance


def music_factory(id_manager: IdManager = Depends(id_manager)):
    
    return MusicFactory(id_manager=id_manager)


job_repository_instance = JobRepository()
def job_repository() -> JobRepository:
    
    return job_repository_instance


def job_factory(id_manager: IdManager = Depends(id_manager)):
    
    return JobFactory(id_manager=id_manager)


def send_conn():
    from src.broker.factory import BrokerConnectionFactory
    return BrokerConnectionFactory.create_connection()


def dispatcher() -> Dispatcher:
    
    return Dispatcher(conn=send_conn())


storage_instance = Storage()
def storage() -> Storage:
    return storage_instance


def music_service(
    music_repository: MusicRepository = Depends(music_repository),
    music_factory: MusicFactory = Depends(music_factory),
    job_repository: JobRepository = Depends(job_repository),
    job_factory: JobFactory = Depends(job_factory),
    storage: Storage = Depends(storage),
    dispatcher: Dispatcher = Depends(dispatcher),
    ) -> MusicService:
    
    return MusicService(
        music_repository=music_repository,
        music_factory=music_factory,
        job_repository=job_repository,
        job_factory=job_factory,
        storage=storage,
        dispatcher=dispatcher
        )


def system_service(
    music_repository: MusicRepository = Depends(music_repository),
    job_repository: JobRepository = Depends(job_repository),
    storage: Storage = Depends(storage),
    dispatcher: Dispatcher = Depends(dispatcher),
    ) -> SystemService:

    return SystemService(
        music_repository=music_repository,
        job_repository=job_repository,
        storage=storage,
        dispatcher=dispatcher
    )


server_worker_manager_instance = None
def server_worker_manager():
    from src.broker.factory import WorkerFactory
    from src.broker.manager import WorkerManager
    global server_worker_manager_instance
    if not server_worker_manager_instance:
        server_worker_manager_instance = WorkerManager(
            workers=[WorkerFactory.create_server()]
            )

    return server_worker_manager_instance

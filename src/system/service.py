

from http import HTTPStatus
import logging
import src.config as config

from fastapi import HTTPException
from src.broker.dispatcher import Dispatcher

from src.music.repository import MusicRepository
from src.storage.storage import Storage
from src.system.job.repository import JobRepository
from src.system.job.schema import JobStatsCreate, JobStatsRead


class SystemService:
    def __init__(
        self,
        music_repository: MusicRepository,
        job_repository: JobRepository,
        storage: Storage,
        dispatcher: Dispatcher
        ) -> None:
        self.music_repository = music_repository
        self.job_repository = job_repository
        self.storage = storage
        self.dispatcher = dispatcher


    def list_all_jobs(self) -> list[int]:

        return list(self.job_repository.cache.keys())


    def job_stats(
        self, 
        schema: JobStatsCreate
        ) -> JobStatsRead:
        try:

            return self.job_repository.get(job_id=schema.job_id).to_schema_job_stats()
        except AttributeError as e:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND) from e


    def reset(self) -> None:
        logging.info('Server: system reboot.')
        self.storage.reset()
        self.dispatcher.send_reset_msg()
        self.job_repository.reset()
        self.music_repository.reset()

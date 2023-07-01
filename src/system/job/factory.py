import time

from torch import Tensor

import src.config as config
from src.music.schema import MusicProcessCreate
from src.system.job.model import JobModel
from src.utils import IdManager


class JobFactory:
    def __init__(
        self,
        id_manager: IdManager
        ) -> None:
        self.id_manager = id_manager
        
    def create_job_model(
        self,
        schema: MusicProcessCreate,
        chunk: bytes,
        chunk_nr: int
        ) -> JobModel:
        
        return JobModel(
            job_id=self.id_manager.next_job_id(),
            size=len(chunk), # audio size
            time=time.time(), # current timestamp
            music_id=schema.music_id,
            track_id=schema.body,
            chunk=chunk,
            chunk_nr=chunk_nr,
            worker_id=-1,
            last_alive=-1.0,
            is_finished=False
            )
    
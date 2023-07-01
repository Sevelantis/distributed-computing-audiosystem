from pydantic import BaseModel
from torch import Tensor
import time
import src.config as config

from src.system.job.schema import JobStatsRead
from src.system.job.message import JobMsg


class JobModel(BaseModel):
    job_id: int
    size:int
    time: int
    music_id:  int
    track_id: list[int]
    chunk: bytes
    chunk_nr: int
    worker_id: int = -1
    last_alive: int
    is_finished: bool

    class Config:
        arbitrary_types_allowed = True


    def to_schema_job_stats(self) -> JobStatsRead:

        return JobStatsRead(
            job_id=self.job_id,
            size=self.size,
            time=self.time,
            music_id=self.music_id,
            track_id=self.track_id
        )


    def to_job_msg(self) -> JobMsg:
        
        return JobMsg(
            music_id=self.music_id,
            job_id=self.job_id,
            chunk=self.chunk,
            chunk_nr=self.chunk_nr
        )

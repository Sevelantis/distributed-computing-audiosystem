from torch import Tensor
from src.broker.message import Message
import src.config as config

class JobMsg(Message):
    def __init__(
        self,
        music_id: int = None,
        job_id: int = None,
        chunk: bytes = None,
        chunk_nr: int = None
        ) -> None:
        super().__init__(action=config.ACTION_JOB_MSG)
        self.music_id = music_id
        self.job_id = job_id
        self.chunk = chunk
        self.chunk_nr = chunk_nr
        

class JobDoneMsg(Message):
    def __init__(
        self,
        music_id: int = None,
        job_id: int = None,
        drums: bytes = None,
        vocals: bytes = None,
        other: bytes = None,
        bass: bytes = None,
        chunk_nr: int = None,
        job_processing_time: float = None
        ) -> None:
        super().__init__(action=config.ACTION_JOB_DONE)
        self.music_id = music_id
        self.job_id = job_id
        self.drums = drums
        self.vocals = vocals
        self.other = other
        self.bass = bass
        self.chunk_nr = chunk_nr
        self.job_processing_time = job_processing_time

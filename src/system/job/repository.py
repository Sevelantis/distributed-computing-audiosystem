from src.system.job.model import JobModel


class JobRepository:
    def __init__(self) -> None:
        self.cache: dict[int, JobModel] = {}
    
    def push(self, job_id: int, model: JobModel) -> None:
        self.cache[job_id] = model

    def pop(self, job_id: int) -> None:
        del self.cache[job_id]

    def get(self, job_id: int) -> JobModel:
        return None if job_id not in self.cache.keys() else self.cache[job_id]

    def find_by_music_id(self, music_id: int) -> list[JobModel]:
        return [ job for job in self.cache.values() if job.music_id == music_id ]

    def find_by_music_id_and_is_finished(self, music_id: int, is_finished: bool) -> list[JobModel]:
        return [ job for job in self.cache.values() if job.music_id == music_id and job.is_finished == is_finished]

    def reset(self) -> None:
        self.cache = {}

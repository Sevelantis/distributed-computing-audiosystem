from pydantic import BaseModel, Field


# stats
class JobStatsCreate(BaseModel):
    job_id: int

class JobStatsRead(BaseModel):
    job_id: int
    size: int
    time: int
    music_id: int
    track_id: list[int]

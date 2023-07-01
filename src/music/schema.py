from fastapi import UploadFile
from pydantic import BaseModel


# progress
class Instrument(BaseModel):
    name: str
    track: str

class MusicProgressCreate(BaseModel):
    music_id: int

class MusicProgressRead(BaseModel):
    progress: int
    instruments: list[Instrument]
    final: str

# process
class MusicProcessCreate(BaseModel):
    music_id: int
    body: list[int]
    
class MusicProcessRead(BaseModel):
    pass

# submit
class Track(BaseModel):
    name: str
    track_id: int

class MusicSubmitCreate(BaseModel):
    body: UploadFile

class MusicSubmitRead(BaseModel):
    music_id: int
    name: str
    band: str
    tracks: list[Track]

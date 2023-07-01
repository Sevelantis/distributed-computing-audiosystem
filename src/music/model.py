from pydantic import BaseModel

from src.music.schema import Instrument, MusicProgressRead, MusicSubmitRead, Track


class InstrumentModel(BaseModel):
    name: str
    track: str

class TrackModel(BaseModel):
    name: str
    track_id: int

class MusicModel(BaseModel):
    music_id:int
    progress:int
    jobs_delivered: int
    jobs_total: int
    instruments:list[InstrumentModel]
    tracks:list[TrackModel]
    final:str
    name: str
    band:str
    uri: str
    parts_drums_uris: list[str]
    parts_vocals_uris: list[str]
    parts_other_uris: list[str]
    parts_bass_uris: list[str]
    processing_time: float

    def to_schema_progress(self) -> MusicProgressRead:

        return MusicProgressRead(
            music_id=self.music_id,
            progress=self.progress,
            instruments=[ Instrument(name=instrument.name, track=instrument.track) for instrument in self.instruments ],
            final=self.final
        )


    def to_schema_submit(self) -> MusicSubmitRead:

        return MusicSubmitRead(
            music_id=self.music_id,
            name=self.name,
            band=self.band,
            tracks=[ Track(name=track.name, track_id=track.track_id) for track in self.tracks]
        )

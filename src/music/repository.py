from src.music.model import MusicModel


class MusicRepository:
    def __init__(self) -> None:
        self.cache: dict[int, MusicModel] = {}
    
    def push(self, music_id: int, model: MusicModel) -> None:
        self.cache[music_id] = model

    def pop(self, music_id: int) -> None:
        del self.cache[music_id]

    def get(self, music_id: int) -> MusicModel:
        return None if music_id not in self.cache.keys() else self.cache[music_id]

    def find_unprocessed(self, min_progress: int = 99) -> list[MusicModel]:
        return [ music for music in self.cache.values() if music.progress < min_progress ]

    def find_instrument_names_by_track_ids(self, music_id: int, track_ids: list[int]) -> str:
        music: MusicModel = self.get(music_id=music_id)
        return [ track.name for track in music.tracks if track.track_id in track_ids]

    def reset(self) -> None:
        self.cache = {}

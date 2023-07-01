

from src.music.model import InstrumentModel, MusicModel, TrackModel
from src.music.schema import MusicSubmitCreate
from src.utils import IdManager
import src.config as config
from src.storage.utils import StorageUtils

class MusicFactory:
    def __init__(
        self,
        id_manager: IdManager
        ) -> None:
        self.id_manager = id_manager
        
    def create_music_model(
        self,
        schema: MusicSubmitCreate
        ) -> MusicModel:
        
        music_id = self.id_manager.next_music_id()
        return MusicModel(
            music_id=music_id,
            progress=-1,
            jobs_total=-1,
            jobs_delivered=0,
            instruments=[ InstrumentModel(name=name, track=config.DEFAULT_URL) for name in config.AUDIO_INSTRUMENTS],
            tracks=[ TrackModel(name=name, track_id=self.id_manager.next_track_id()) for name in config.AUDIO_INSTRUMENTS ],
            final=config.DEFAULT_URL,
            name=config.DEFAULT_TMP_SONG,
            band=config.DEFAULT_TMP_BAND,
            uri=StorageUtils.get_submit_music_uri(
                music_id=music_id
            ),
            parts_drums_uris=[],
            parts_vocals_uris=[],
            parts_other_uris=[],
            parts_bass_uris=[],
            processing_time=-1.0
        )
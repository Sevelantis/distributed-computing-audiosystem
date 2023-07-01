import src.config as config

MUSIC_TAG = 'music-id'
CHUNK_TAG = 'chunk-nr'
TRACK_IDS_TAG = 'track-ids'
WORKER_TAG = 'worker-id'


class StorageUtils:


    @classmethod
    def get_server_music_work_dir_uri(cls, music_id: int) -> str:

        return f'{config.STORAGE_SERVER_DIR}/{MUSIC_TAG}_{music_id}'


    @classmethod
    def get_worker_work_dir_uri(cls, worker_id: int) -> str:

        return f'{config.STORAGE_WORKER_DIR}/{WORKER_TAG}_{worker_id}'


    @classmethod    
    def get_submit_music_uri(
        cls,
        music_id: int,
        ) -> str:

        return f'{cls.get_server_music_work_dir_uri(music_id)}/{config.STORAGE_MODE_SUBMITTED}.{config.AUDIO_EXT_MP3}'


    @classmethod    
    def get_tmp_part_server_uri(
        cls,
        music_id: int,
        chunk_nr: int,
        instrument_name: str
        ) -> str:
        
        return f'{cls.get_server_music_work_dir_uri(music_id)}/tmp_part_{CHUNK_TAG}_{str(chunk_nr).zfill(4)}_{instrument_name}.{config.AUDIO_EXT_MP3}'


    @classmethod    
    def get_tmp_tensor_wav_uri(
        cls,
        worker_id: int,
        chunk_nr: int,
        instrument_name: str
        ) -> str:
        
        return f'{cls.get_worker_work_dir_uri(worker_id)}/tmp_{config.STORAGE_MODE_PROCESSED}_{CHUNK_TAG}_{str(chunk_nr).zfill(4)}_{instrument_name}.{config.AUDIO_EXT_WAV}'


    @classmethod
    def get_tmp_chunk_uri(cls, worker_id: int, chunk_nr: int):
        
        return f'{cls.get_worker_work_dir_uri(worker_id)}/tmp_chunk_{CHUNK_TAG}_{str(chunk_nr).zfill(4)}.{config.AUDIO_EXT_MP3}'


    @classmethod
    def get_final_mix_uri(cls, music_id: int, instrument_names: list[str]) -> str:
        instrument_names_human_read = '_'.join(instrument_names)

        return f'{cls.get_server_music_work_dir_uri(music_id)}/{config.STORAGE_MODE_FINAL_MIX}_{instrument_names_human_read}.{config.AUDIO_EXT_MP3}'


    @classmethod
    def get_separated_instrument_uri(cls, music_id: int, instrument_name: str) -> str:
        
        return f'{cls.get_server_music_work_dir_uri(music_id)}/{config.STORAGE_MODE_SEPARATE}_{instrument_name}.{config.AUDIO_EXT_MP3}'


    @classmethod
    def get_tmp_parts_uris(cls, music_id: int, chunk_nr: int) -> dict:
        parts_uris = {}
        for instrument_name in config.AUDIO_INSTRUMENTS:
            parts_uris[instrument_name] = cls.get_tmp_part_server_uri(
                music_id=music_id,
                chunk_nr=chunk_nr,
                instrument_name=instrument_name
            )

        return parts_uris


    @classmethod
    def get_separated_instruments_uris(cls, music_id: int) -> dict:
        merged_parts_uris = {}
        for instrument_name in config.AUDIO_INSTRUMENTS:
            merged_parts_uris[instrument_name] = cls.get_separated_instrument_uri(
                music_id=music_id,
                instrument_name=instrument_name
            )

        return merged_parts_uris


    @classmethod
    def get_url_from_uri(cls, uri: str) -> str:
        
        return f'http://{config.APP_HOST}:{config.APP_PORT}/{config.AUDIO_EXT_MP3}/{uri}'

import time

from src.music.utils import AudioUtils
from src.storage.storage import Storage
from tests.test_base import *
from src.system.job.message import JobMsg
from src.audio_worker.listener import AudioWorkerListener


@pytest.fixture()
def storage_mock() -> Storage:
    return Storage()


def test_save_from_upload_file(
    storage_mock: Storage,
    upload_file_mock: UploadFile
    ):
    target_uri='upload_storage/new.wav'
    '''
    UploadFile is an object that is created when the user submits his mp3 audio (or any other binary data...)
    '''    
    start = time.time()
    storage_mock.save_bytes_audio_to_uri(
        audio_file=upload_file_mock,
        uri=target_uri
        )
    diff = time.time() - start
    
    assert True
    
    
def test_retrieve_mp3_metadata_from_uri(
    uri='tracks/test.mp3'
    ):
    start = time.time()
    mp3_meta = AudioUtils.retrieve_audio_meta_from_uri(uri=uri)
    diff = time.time() - start

    assert True

def test_process_music(
    storage_mock: Storage,
    uri='tracks/test.mp3'
    ):
    assert isinstance(storage_mock, Storage)

    start = time.time()
    chunks: list[bytes] = AudioUtils.split_audio_to_chunks_from_uri(uri=uri)
    # send chunks
    parts: dict = {}
    for i in range(len(chunks)):
        # chunk received
        chunk_uri = f'{config.STORAGE_WORKER_DIR}/tmp_chunk_{i}.mp3'
        storage_mock.save_bytes_audio_to_uri(
            data=chunks[i],
            uri=chunk_uri
        )
        separate_instruments = AudioUtils.separate_instruments_from_uri(
            uri=chunk_uri
            )

        # save separated instruments as wav
        for tensor, name in separate_instruments:
            instrument_uri = f'{config.STORAGE_WORKER_DIR}/tmp_{config.STORAGE_MODE_PROCESSED}_{i}_{name}.wav'
            storage_mock.save_tensor_wav_to_uri(
                tensor=tensor,
                uri=instrument_uri,
                samplerate=AudioUtils.get_model().samplerate            
            )

        # load instruments as bytes
        drums_uri = f'{config.STORAGE_WORKER_DIR}/tmp_{config.STORAGE_MODE_PROCESSED}_{i}_drums.wav'
        vocals_uri = f'{config.STORAGE_WORKER_DIR}/tmp_{config.STORAGE_MODE_PROCESSED}_{i}_vocals.wav'
        other_uri = f'{config.STORAGE_WORKER_DIR}/tmp_{config.STORAGE_MODE_PROCESSED}_{i}_other.wav'
        bass_uri = f'{config.STORAGE_WORKER_DIR}/tmp_{config.STORAGE_MODE_PROCESSED}_{i}_bass.wav'
        drums_bytes = AudioUtils.load_bytes_from_uri(uri=drums_uri)
        vocals_bytes = AudioUtils.load_bytes_from_uri(uri=vocals_uri)
        other_bytes = AudioUtils.load_bytes_from_uri(uri=other_uri)
        bass_bytes = AudioUtils.load_bytes_from_uri(uri=bass_uri)

        # send job done messages
        parts[i] = {
            'drums': drums_bytes,
            'vocals': vocals_bytes,
            'other': other_bytes,
            'bass': bass_bytes,
        }
    parts_drums_uris = []
    parts_vocals_uris = []
    parts_other_uris = []
    parts_bass_uris = []
    for k, v in parts.items():
        drums_uri = f'{config.STORAGE_SERVER_DIR}/tmp_parts_{k}_drums.wav'
        vocals_uri = f'{config.STORAGE_SERVER_DIR}/tmp_parts_{k}_vocals.wav'
        other_uri = f'{config.STORAGE_SERVER_DIR}/tmp_parts_{k}_other.wav'
        bass_uri = f'{config.STORAGE_SERVER_DIR}/tmp_parts_{k}_bass.wav'
        storage_mock.save_bytes_audio_to_uri(
            data=v['drums'],
            uri=drums_uri
        )
        storage_mock.save_bytes_audio_to_uri(
            data=v['vocals'],
            uri=vocals_uri
        )
        storage_mock.save_bytes_audio_to_uri(
            data=v['other'],
            uri=other_uri
        )
        storage_mock.save_bytes_audio_to_uri(
            data=v['bass'],
            uri=bass_uri
        )
        parts_drums_uris.append(drums_uri)
        parts_vocals_uris.append(vocals_uri)
        parts_other_uris.append(other_uri)
        parts_bass_uris.append(bass_uri)

    merged_drums = AudioUtils.merge_chunks_from_uris(uris=parts_drums_uris)
    merged_vocals = AudioUtils.merge_chunks_from_uris(uris=parts_vocals_uris)
    merged_other = AudioUtils.merge_chunks_from_uris(uris=parts_other_uris)
    merged_bass = AudioUtils.merge_chunks_from_uris(uris=parts_bass_uris)
    storage_mock.save_bytes_audio_to_uri(
        data=merged_drums,
        uri=f'{config.STORAGE_SERVER_DIR}/merged_drums.mp3'
    )
    storage_mock.save_bytes_audio_to_uri(
        data=merged_vocals,
        uri=f'{config.STORAGE_SERVER_DIR}/merged_vocals.mp3'
    )
    storage_mock.save_bytes_audio_to_uri(
        data=merged_other,
        uri=f'{config.STORAGE_SERVER_DIR}/merged_other.mp3'
    )
    storage_mock.save_bytes_audio_to_uri(
        data=merged_bass,
        uri=f'{config.STORAGE_SERVER_DIR}/merged_bass.mp3'
    )

    diff = time.time() - start
    

def test_mix_wavs_from_uris(
    storage_mock: Storage,
    instrument_uris=[
        f'{config.STORAGE_SERVER_DIR}/merged_drums.wav',
        f'{config.STORAGE_SERVER_DIR}/merged_bass.wav',
    ]
    ):
    assert isinstance(storage_mock, Storage)
    
    mix = AudioUtils.mix_wavs_from_uris(uris=instrument_uris)
    storage_mock.save_bytes_audio_to_uri(
        data=mix,
        uri=f'{config.STORAGE_SERVER_DIR}/MIX.wav'
    )


def test_clean_work_dir_tmp_files(
    storage_mock: Storage
    ):
    assert isinstance(storage_mock, Storage)
    
    storage_mock.clean_work_dir_tmp_files(
        work_dir=config.STORAGE_SERVER_DIR
    )


def test_save_bytes_audio_to_uri(
    storage_mock: Storage,
    upload_file_mock: UploadFile,
    work_dir: str = f'{config.STORAGE_WORKER_DIR}/worker-id_1'
    ):
    assert isinstance(storage_mock, Storage)
    assert isinstance(upload_file_mock, UploadFile)
    
    storage_mock.save_bytes_audio_to_uri(
        data=upload_file_mock.file.read(),
        uri=f'{work_dir}/tmp_chunk_1.mp3'
    )
    

@pytest.fixture()
def job_msg_mock(
    upload_file_mock: UploadFile
    ):
    
    return JobMsg(
        music_id=999,
        job_id=666,
        chunk=upload_file_mock.file.read(),
        chunk_nr=444
    )


def test_process_parts(
    storage_mock: Storage,
    job_msg_mock: JobMsg,
    work_dir: str = f'{config.STORAGE_WORKER_DIR}/worker-id_333'
    ):
    assert isinstance(storage_mock, Storage)
    assert isinstance(job_msg_mock, JobMsg)

    chunk_uri = f'{work_dir}/tmp_chunk_{job_msg_mock.chunk_nr}.mp3'
    storage_mock.save_bytes_audio_to_uri(
        data=job_msg_mock.chunk,
        uri=chunk_uri
    )
    separate_instruments = AudioUtils.separate_instruments_from_uri(
        uri=chunk_uri
        )
    parts = {}
    for tensor, instrument_name in separate_instruments:
        part_uri = f'{work_dir}/tmp_{config.STORAGE_MODE_PROCESSED}_{job_msg_mock.chunk_nr}_{instrument_name}.wav'
        storage_mock.save_tensor_wav_to_uri(
            tensor=tensor,
            uri=part_uri,
            samplerate=AudioUtils.get_model().samplerate            
        )
        debug_tensor_size = AudioUtils.retrieve_tensor_meta(tensor=tensor)['size']
        parts[instrument_name] = AudioUtils.load_bytes_from_uri(
            uri=part_uri
            )
    
    for key, value in parts.items():
        debug_part_size = len(value)
        assert key in config.AUDIO_INSTRUMENTS, f"Key '{key}' is not present in the dictionary."
        assert isinstance(value, bytes), f"Value for key '{key}' is not of type 'bytes'."

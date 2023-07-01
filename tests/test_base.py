import io

import pytest
from demucs.apply import BagOfModels, apply_model
from fastapi import UploadFile
from fastapi.testclient import TestClient

import src.config as config
from src.music.model import InstrumentModel, MusicModel, TrackModel
from src.music.repository import MusicRepository
from src.music.utils import AudioUtils
from src.main import app


@pytest.fixture()
def upload_file_mock() -> UploadFile:
    with open('tracks/test.mp3', 'rb') as f:
        size = len(f.read())
        return UploadFile(
            filename='test.mp3',
            file=io.BytesIO(f.read()),
            headers={"content-type": "audio/mpeg"},
        )

@pytest.fixture()
def music_model_mock(
    upload_file_mock: UploadFile
):
    return MusicModel(
        music_id=1,
        progress=44,
        instruments=[
            InstrumentModel(name='drums', track='URL to drums'),
            InstrumentModel(name='vocals', track='URL to vocals'),
            ],
        tracks=[
            TrackModel(name='drums', track_id=1),
            TrackModel(name='vocals', track_id=2)
        ],
        final='final URL with the mix',
        name='song name',
        band='band',
        uri='upload_storage/new.wav'
    )
    
@pytest.fixture()
def music_repository_mock():
    return MusicRepository()
    
@pytest.fixture()
def client():
    return TestClient(app)

@pytest.fixture()
def model_mock():
    return AudioUtils.get_model()

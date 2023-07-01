import pytest

from src.music.model import MusicModel
from src.music.repository import MusicRepository
from tests.test_base import *


def test_get_item_from_repo(
    music_repository_mock: MusicRepository,
    music_model_mock: MusicModel
    ):
    assert isinstance(music_repository_mock, MusicRepository)
    assert isinstance(music_model_mock, MusicModel)

    assert music_repository_mock.get(music_model_mock.music_id) is None

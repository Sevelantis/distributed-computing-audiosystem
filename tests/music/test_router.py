import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from src.music.model import MusicModel
from tests.test_base import *


@pytest.fixture()
def music_router():
    from src.music.router import music_router
    return music_router

def test_list_all(
    music_router: APIRouter,
    music_model_mock: MusicModel,
    client: TestClient
    ):
    assert isinstance(music_router, APIRouter)
    assert isinstance(music_model_mock, MusicModel)
    assert isinstance(client, TestClient)
    
    response = client.get('/music')
    assert response.status_code == 200
    x = response.json()
    y =1
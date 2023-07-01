
from http import HTTPStatus
import logging
import time
from fastapi import HTTPException
from src.broker.dispatcher import Dispatcher
from src.music.utils import AudioUtils
from src.music.factory import MusicFactory
from src.music.model import MusicModel
from src.music.repository import MusicRepository
from src.music.schema import MusicProcessCreate, MusicProcessRead, MusicProgressCreate, MusicProgressRead, MusicSubmitCreate, MusicSubmitRead
import src.config as config
from src.storage.storage import Storage
from src.system.job.factory import JobFactory
from src.system.job.model import JobModel
from src.system.job.repository import JobRepository

class MusicService():
    def __init__(
        self,
        music_repository: MusicRepository,
        music_factory: MusicFactory,
        job_factory: JobFactory,
        job_repository: JobRepository,
        storage: Storage,
        dispatcher: Dispatcher,
        ) -> None:
        self.music_repository = music_repository
        self.music_factory = music_factory
        self.job_factory = job_factory
        self.storage = storage
        self.job_repository = job_repository
        self.dispatcher = dispatcher


    def list_all(self) -> list[MusicSubmitRead]:
        return [ music_model.to_schema_submit() for music_model in self.music_repository.cache.values() ]


    def submit(
        self,
        schema: MusicSubmitCreate
        ) -> MusicSubmitRead:
        '''
        Adds new song to the system.
        '''
        music_model: MusicModel = self.music_factory.create_music_model(schema=schema)
        
        self.storage.save_bytes_audio_to_uri(
            data=schema.body.file.read(),
            uri=music_model.uri,
        )
        
        audio_tags = AudioUtils.retrieve_audio_meta_from_uri(uri=music_model.uri)
        music_model.band = audio_tags.artist if audio_tags.artist else config.DEFAULT_UNKNOWN_BAND
        music_model.name = audio_tags.title if audio_tags.title else config.DEFAULT_UNKNOWN_SONG
        
        self.music_repository.push(
            music_id=music_model.music_id,
            model=music_model
        )
        try:
            
            return music_model.to_schema_submit()
        except AttributeError as e:
            raise HTTPException(status_code=HTTPStatus.METHOD_NOT_ALLOWED) from e


    def process(
        self,
        schema: MusicProcessCreate
        ) -> MusicProcessRead:
        music = self.music_repository.get(music_id=schema.music_id)
        if not music:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        instrument_names = self.music_repository.find_instrument_names_by_track_ids(
            music_id=schema.music_id,
            track_ids=schema.body
        )
        if not instrument_names:
            raise HTTPException(status_code=HTTPStatus.METHOD_NOT_ALLOWED)
        
        logging.info(f'Splitting audio to chunks...')
        # split audio to N chunks
        chunks: list[bytes] = AudioUtils.split_audio_to_chunks_from_uri(
            uri=music.uri
            )
        
        # update music model
        chunks_total = len(chunks)
        music.progress = 0
        music.jobs_total = chunks_total
        music.processing_time = time.time()
        
        # create and save job models
        for i in range(chunks_total):
            job: JobModel = self.job_factory.create_job_model(
                schema=schema,
                chunk=chunks[i],
                chunk_nr=i
            )
            self.job_repository.push(
                job_id=job.job_id,
                model=job
                )
        jobs = self.job_repository.find_by_music_id(music_id=music.music_id)
        job_messages = [ job.to_job_msg() for job in jobs ]
        # send job messages
        logging.info(f'MusicService: Music[{music.music_id}]: Sending {len(jobs)} jobs')
        for msg in job_messages:
            self.dispatcher.send_job_msg(msg=msg)        

        return MusicProcessRead()


    def progress(
        self,
        schema: MusicProgressCreate
        ) -> MusicProgressRead:
        try:

            return self.music_repository.get(music_id=schema.music_id).to_schema_progress()
        except AttributeError as e:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND) from e

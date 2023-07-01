import logging
import queue
import threading
import time

import stomp
import stomp.connect as connect
import stomp.utils

import src.config as config
from src.broker.dispatcher import Dispatcher
from src.broker.serializer import MessageSerializer
from src.music.model import MusicModel
from src.music.repository import MusicRepository
from src.music.utils import AudioUtils
from src.storage.storage import Storage
from src.storage.utils import StorageUtils
from src.system.job.message import JobDoneMsg
from src.system.job.model import JobModel
from src.system.job.repository import JobRepository


class ServerListener(stomp.ConnectionListener):
    def __init__(
        self,
        conn: connect.StompConnection11,
        dispatcher: Dispatcher,
        music_repository: MusicRepository,
        job_repository: JobRepository,
        storage: Storage,
        server_id: str,
        ) -> None:
        self.conn = conn
        self.dispatcher = dispatcher
        self.music_repository = music_repository
        self.job_repository = job_repository
        self.storage = storage
        self.server_id = server_id
        
        self.job_done_queue = queue.Queue()
        self.j_done_thread = threading.Thread(target=self.job_done_thread)


    def on_message(self, frame: stomp.utils.Frame):
        destination = frame.headers.get('destination')
        if config.BROKER_JOB_DONE_QUEUE in destination:
            self.job_done_queue.put(frame)


    def job_done_thread(self) -> None:
        while True:
            time.sleep(0.1)
            if not self.job_done_queue.empty():
                frame: stomp.utils.Frame = self.job_done_queue.get()
                msg: JobDoneMsg = MessageSerializer.deserialize_job_done_msg(
                    serialized_msg=frame.body
                )
                job: JobModel = self.process_job_done_msg(msg=msg)
                self.conn.ack(id=frame.headers.get('message-id'), subscription=frame.headers.get('subscription'))
                if job:
                    logging.info(f'Server: JobDoneMsg[{job.job_id}] - ACK - job time: {format(msg.job_processing_time, ".2f")}[s]')
                else:
                    logging.info(f'Server: JobDoneMsg[{msg.job_id}] - delivered, but does not exist.')


    def process_job_done_msg(self, msg: JobDoneMsg) -> JobModel:
        job: JobModel = self.job_repository.get(
            job_id=msg.job_id
        )
        music: MusicModel = self.music_repository.get(
            music_id=msg.music_id
        )
        if not job or not music:
            return None
        parts_uris = StorageUtils.get_tmp_parts_uris(
            music_id=msg.music_id,
            chunk_nr=msg.chunk_nr
            )
        self.save_parts(
            parts_uris=parts_uris,
            job_done_msg=msg
        )        
        self.update_repositories_on_job_done(
            music=music,
            job=job,
            msg=msg,
            parts_uris=parts_uris
        )
        logging.info(f'Server: Music[{music.music_id}] - Progress: {music.progress}%.')
        if music.progress == 99:
            self.finish_him(
                music=music,
                job=job,
                msg=msg
            )
        elif music.progress > 99:
            logging.error(
                f'Server: Music[{music.music_id}] Redundant job was delivered.')
        
        return job


    def finish_him(self, music: MusicModel, job: JobModel, msg: JobDoneMsg) -> None:
        start = time.time()
        logging.info('Server: Merging chunks...')
        separated_instruments = self.merge_parts(music)
        merge_time = time.time() - start
        logging.info(f'Server: Music[{music.music_id}] - merge time: {format(merge_time, ".2f")}[s]')
        separated_instruments_uris = StorageUtils.get_separated_instruments_uris(
            music_id=music.music_id
        )
        self.save_separated_instruments(
            separated_instruments=separated_instruments,
            separated_instruments_uris=separated_instruments_uris
        )
        instrument_names = [ track.name for track in music.tracks if track.track_id in job.track_id]
        final_mix = AudioUtils.mix_wavs_from_uris(
            uris= [ separated_instruments_uris[name] for name in instrument_names ]
        )
        final_mix_uri = StorageUtils.get_final_mix_uri(
                music_id=music.music_id,
                instrument_names=instrument_names
            )
        self.storage.save_bytes_audio_to_uri(
            data=final_mix,
            uri=final_mix_uri
        )
        self.update_music_uris(
            music=music,
            final_mix_uri=final_mix_uri,
            separated_instruments_uris=separated_instruments_uris
            )
        music.progress = 100
        music.processing_time = time.time() - music.processing_time
        logging.info(f'Server: Music[{music.music_id}] - total time: {format(music.processing_time, ".2f")}[s]')
        
        self.clean_workspace_for_music(music=music)


    def update_repositories_on_job_done(self, music: MusicModel, job: JobModel, msg: JobDoneMsg, parts_uris: dict) -> None:
        job.time = msg.job_processing_time
        job.is_finished = True
        music.jobs_delivered += 1
        music.progress = int( music.jobs_delivered * 100 / music.jobs_total )
        if music.progress == 100:
            music.progress = 99
        music.parts_drums_uris.append(parts_uris['drums'])
        music.parts_vocals_uris.append(parts_uris['vocals'])
        music.parts_other_uris.append(parts_uris['other'])
        music.parts_bass_uris.append(parts_uris['bass'])


    def save_separated_instruments(self, separated_instruments: dict, separated_instruments_uris: dict) -> None:
        for instrument_name in config.AUDIO_INSTRUMENTS:
            self.storage.save_bytes_audio_to_uri(
                data=separated_instruments[instrument_name],
                uri=separated_instruments_uris[instrument_name]
            )


    def merge_parts(self, music: MusicModel) -> dict:
    
        return {
            'drums': AudioUtils.merge_chunks_from_uris(uris=music.parts_drums_uris),
            'vocals': AudioUtils.merge_chunks_from_uris(uris=music.parts_vocals_uris),
            'other': AudioUtils.merge_chunks_from_uris(uris=music.parts_other_uris),
            'bass': AudioUtils.merge_chunks_from_uris(uris=music.parts_bass_uris)
        }


    def save_parts(self, parts_uris: dict, job_done_msg: JobDoneMsg) -> None:
        self.storage.save_bytes_audio_to_uri(
            data=job_done_msg.drums,
            uri=parts_uris['drums']
        )
        self.storage.save_bytes_audio_to_uri(
            data=job_done_msg.vocals,
            uri=parts_uris['vocals']
        )
        self.storage.save_bytes_audio_to_uri(
            data=job_done_msg.other,
            uri=parts_uris['other']
        )
        self.storage.save_bytes_audio_to_uri(
            data=job_done_msg.bass,
            uri=parts_uris['bass']
        )


    def update_music_uris(self, music: MusicModel, final_mix_uri: str, separated_instruments_uris: str) -> None:
        music.final = StorageUtils.get_url_from_uri(uri=final_mix_uri)
        for instrument in music.instruments:
            if instrument.name in separated_instruments_uris:
                instrument.track = StorageUtils.get_url_from_uri(uri=separated_instruments_uris[instrument.name])


    def clean_workspace_for_music(self, music: MusicModel) -> None:
        self.storage.clean_work_dir_tmp_files(
            work_dir=StorageUtils.get_server_music_work_dir_uri(
                music_id=music.music_id
                )
            )
        logging.info(f'Server: Music[{music.music_id}] - cleaning workspace.')

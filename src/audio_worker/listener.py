import concurrent
import concurrent.futures
import logging
import queue
import threading
import time
from threading import Lock

import stomp
import stomp.connect as connect
import stomp.utils

import src.config as config
from src.broker.dispatcher import Dispatcher
from src.broker.serializer import MessageSerializer
from src.music.utils import AudioUtils
from src.storage.storage import Storage
from src.storage.utils import StorageUtils
from src.system.job.message import JobDoneMsg, JobMsg


class AudioWorkerListener(stomp.ConnectionListener):
    def __init__(
        self,
        conn: connect.StompConnection11,
        dispatcher: Dispatcher,
        storage: Storage,
        worker_id: int,
        ) -> None:
        self.conn = conn
        self.dispatcher = dispatcher
        self.storage = storage
        self.processing = False
        self.worker_id = worker_id
        self.clean_workspace()
        self.job_queue = queue.Queue()
        self.j_thread = threading.Thread(target=self.job_thread)
        self.job_frame_meta: tuple[str, str, int] = (None, None, None)
        self.was_cancelled = False
        self.lock = threading.Lock()


    def on_message(self, frame: stomp.utils.Frame):
        destination = frame.headers.get('destination')
        if destination == f'/queue/{config.BROKER_JOB_QUEUE}':
            self.job_queue.put(frame)

        if  destination == f'/exchange/{config.BROKER_RESET_EXCHANGE}':
            self.process_reset(frame=frame)
            self.conn.ack(id=frame.headers.get('message-id'), subscription=frame.headers.get('subscription'))
            logging.debug(f'Worker[{self.worker_id}]: ResetMsg - ACK')


    def job_thread(self) -> None:
        while True:
            time.sleep(0.5)
            if not self.job_queue.empty():
                frame: stomp.utils.Frame = self.job_queue.get()
                msg: JobMsg = MessageSerializer.deserialize_job_msg(
                    serialized_msg=frame.body
                    )
                self.job_frame_meta = (frame.headers.get('message-id'), frame.headers.get('subscription'), msg.job_id)
                job_done_msg = None
                try:
                    job_done_msg = self.process_job(msg=msg)
                except Exception as e:
                    self.conn.nack(id=self.job_frame_meta[0] , subscription=self.job_frame_meta[1])
                    self.job_frame_meta = (None, None, None)
                    logging.error(f'Worker[{self.worker_id}]: Error while processing parts:')
                    return                    
                if not self.was_cancelled:
                    self.dispatcher.send_job_done_msg(msg=job_done_msg)
                    self.conn.ack(id=self.job_frame_meta[0] , subscription=self.job_frame_meta[1])
                    logging.info(f'Worker[{self.worker_id}]: Job[{job_done_msg.job_id}] - JobDoneMsg - ACK')
                    self.clean_workspace()
                else:
                    with self.lock:
                        self.was_cancelled = False
                    logging.info(f'Worker[{self.worker_id}]: Reset successfull. Ready for new jobs.')
                self.job_frame_meta = (None, None, None)


    def process_job(self, msg: JobMsg) -> JobDoneMsg:
        start = time.time()
        parts = None
        parts = self.process_parts(msg=msg)
        proc_time = time.time() - start
        return JobDoneMsg(
                music_id=msg.music_id,
                job_id=msg.job_id,
                drums=parts['drums'],
                vocals=parts['vocals'],
                other=parts['other'],
                bass=parts['bass'],
                chunk_nr=msg.chunk_nr,
                job_processing_time=proc_time
            )


    def process_reset(self, frame: stomp.utils.Frame) -> None:
        if self.job_frame_meta[0] and self.job_frame_meta[1] and self.job_frame_meta[2]:
            with self.lock:
                self.was_cancelled = True
            logging.info(f'Worker[{self.worker_id}]: Cancel received. Removing job from the queue. Waiting for job to finish...')
            self.conn.ack(id=self.job_frame_meta[0], subscription=self.job_frame_meta[1])
        else:
            logging.info(f'Worker[{self.worker_id}]: cancel received. No jobs - resetting.')
            self.clean_workspace()


    def process_parts(self, msg: JobMsg) -> dict:
        logging.info(f'Worker[{self.worker_id}] started Job[{msg.job_id}].')
        chunk_uri = StorageUtils.get_tmp_chunk_uri(
            worker_id=self.worker_id,
            chunk_nr=msg.chunk_nr
        )
        self.storage.save_bytes_audio_to_uri(
            data=msg.chunk,
            uri=chunk_uri
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future_instruments: concurrent.futures.Future = executor.submit(
                lambda: AudioUtils.separate_instruments_from_uri(
                    self.worker_id,
                    chunk_uri
                    )
                )
            concurrent.futures.wait([future_instruments])
            if future_instruments.done():
                separate_instruments = future_instruments.result()
                if not separate_instruments:
                    return None

        parts = {}
        for tensor, instrument_name in separate_instruments:
            tensor_uri = StorageUtils.get_tmp_tensor_wav_uri(
                worker_id=self.worker_id,
                chunk_nr=msg.chunk_nr,
                instrument_name=instrument_name
            )
            self.storage.save_tensor_wav_to_uri(
                tensor=tensor,
                uri=tensor_uri,
                samplerate=AudioUtils.get_model().samplerate            
            )
            parts[instrument_name] = AudioUtils.load_bytes_from_uri(
                uri=tensor_uri
                )

        return parts


    def clean_workspace(self) -> None:
        self.storage.clean_work_dir_tmp_files(
            work_dir=StorageUtils.get_worker_work_dir_uri(worker_id=self.worker_id)
            )
        logging.debug(f'Worker[{self.worker_id}] workspace clean.')

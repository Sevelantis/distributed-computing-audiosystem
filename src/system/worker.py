import logging
import time

import stomp.connect as connect

import src.config as config
from src.music.repository import MusicRepository
from src.broker.dispatcher import Dispatcher
from src.broker.utils import BrokerUtils
from src.storage.storage import Storage
from src.system.listener import ServerListener
from src.system.job.repository import JobRepository


class Server:
    def __init__(
        self, 
        connection: connect.StompConnection11,
        dispatcher: Dispatcher,
        storage: Storage,
        music_repository: MusicRepository,
        job_repository: JobRepository,
        ) -> None:
        self.conn = connection
        self.dispatcher = dispatcher
        self.storage = storage
        self.music_repository = music_repository
        self.job_repository = job_repository
        self.stopped = False
        self.server_id = BrokerUtils.generate_id()
        self.listener: ServerListener = None
        self.__setup()


    def loop(self) -> None:
        while True:
            time.sleep(config.WORKER_THREAD_INTERVAL)
            if self.stopped:
                logging.warn(f'Server[{self.server_id}]: disconnected.')
                break
        self.listener.j_done_thread.join()
        logging.warn(f'Server[{self.server_id}]: exited main thread.')


    def stop(self) -> None:
        self.stopped = True


    def __setup(self):
        self.conn.subscribe(
            destination=config.BROKER_JOB_DONE_QUEUE,
            id=self.server_id,
            ack='client',
        )
        self.listener = ServerListener(
                conn=self.conn,
                dispatcher=self.dispatcher,
                storage=self.storage,
                music_repository=self.music_repository,
                job_repository=self.job_repository,
                server_id=self.server_id
            )
        self.listener.j_done_thread.start()
        self.conn.set_listener(
            name=f'server_listener_{self.server_id}',
            listener=self.listener
        )


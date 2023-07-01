import logging
import time

import stomp.connect as connect

import src.config as config
from src.audio_worker.listener import AudioWorkerListener
from src.broker.dispatcher import Dispatcher
from src.broker.utils import BrokerUtils
from src.storage.storage import Storage


class AudioWorker:
    def __init__(
        self, 
        connection: connect.StompConnection11, 
        dispatcher: Dispatcher,
        storage: Storage,
        ) -> None:
        self.conn = connection
        self.dispatcher = dispatcher
        self.storage = storage
        self.stopped = False
        self.worker_id = BrokerUtils.generate_id()
        self.listener : AudioWorkerListener = None
        self.__setup()


    def loop(self) -> None:
        while True:
            time.sleep(config.WORKER_THREAD_INTERVAL)
            if self.stopped:
                break
        self.listener.j_thread.join()
        logging.warn(f'Worker[{self.worker_id}]: exited main thread.')


    def stop(self) -> None:
        self.stopped = True


    def __setup(self):
        self.conn.subscribe(
            destination=config.BROKER_JOB_QUEUE,
            id=BrokerUtils.generate_id(),
            ack='client-individual',
            headers={'prefetch-count': 1}
        )
        self.conn.subscribe(
            destination=f'/exchange/{config.BROKER_RESET_EXCHANGE}',
            id=BrokerUtils.generate_id(),
            ack='client-individual'
        )
        self.listener = AudioWorkerListener(
            conn=self.conn,
            dispatcher=self.dispatcher,
            storage=self.storage,
            worker_id=self.worker_id
            )
        self.listener.j_thread.start()
        self.conn.set_listener(
            name=f'audio_worker_listener_{self.worker_id}',
            listener=self.listener
        )
        self.conn.heartbeats = config.AUDIO_WORKER_CONN_HEARTBEATS


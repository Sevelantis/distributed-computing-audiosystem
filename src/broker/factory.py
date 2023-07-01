import logging

import stomp
import stomp.connect as connect
from src.audio_worker.worker import AudioWorker
from src.system.worker import Server

import src.config as config
from src.broker.utils import BrokerUtils
from src.dependencies import dispatcher, job_repository, music_repository, storage


class BrokerConnectionFactory:
    
    @classmethod
    def create_connection(
        cls, 
        broker_host: str = config.BROKER_HOST, 
        broker_port: int = int(config.BROKER_PORT), 
        broker_username: str = config.BROKER_USERNAME, 
        broker_password: str = config.BROKER_PASSWORD, 
        ssl_active: bool=False
        ) -> connect.StompConnection11:
        conn = stomp.Connection(host_and_ports=[(broker_host, broker_port)])
        conn.connect(
            broker_username, 
            broker_password, 
            wait=True
        )
        
        return conn

class WorkerFactory:

    @classmethod
    def create_audio_worker(cls) -> AudioWorker:

        return AudioWorker(
            connection=BrokerConnectionFactory.create_connection(),
            dispatcher=dispatcher(),
            storage=storage(),
        )

    @classmethod
    def create_server(cls) -> Server:

        return Server(
            connection=BrokerConnectionFactory.create_connection(),
            dispatcher=dispatcher(),
            storage=storage(),
            music_repository=music_repository(),
            job_repository=job_repository(),
        )

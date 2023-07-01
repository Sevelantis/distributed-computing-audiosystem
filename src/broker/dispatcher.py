import stomp.connect as connect

import src.config as config
from src.broker.serializer import MessageSerializer
from src.system.job.message import JobDoneMsg, JobMsg
from src.system.message import WorkerResetMsg


class Dispatcher:
    def __init__(self, conn: connect.StompConnection11) -> None:
        self.conn = conn


    def send_job_msg(self, msg: JobMsg) -> None:
        '''server -> worker'''
        self.conn.send(
            destination=config.BROKER_JOB_QUEUE,
            body=MessageSerializer.serialize_job_msg(msg=msg),
            headers={
                'content-type': 'multipart/mixed',
                'action': msg.action
                }
        )


    def send_job_done_msg(self, msg: JobDoneMsg) -> None:
        '''worker -> server'''
        self.conn.send(
            destination=config.BROKER_JOB_DONE_QUEUE,
            body=MessageSerializer.serialize_job_done_msg(msg=msg),
            headers={
                'content-type': 'multipart/mixed',
                'action': msg.action
            }
        )


    def send_reset_msg(self) -> None:
        '''server -> worker'''
        self.conn.send(
            destination=f'/exchange/{config.BROKER_RESET_EXCHANGE}',
            body='reset',
            headers={
                'content-type': 'multipart/mixed'
            }
        )

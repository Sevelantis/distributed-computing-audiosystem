import src.config as config
from src.broker.message import Message


class WorkerResetMsg(Message):
    def __init__(
        self,
        worker_id: str
        ) -> None:
        super().__init__(action=config.ACTION_RESET_WORKER_MSG)
        self.worker_id = worker_id

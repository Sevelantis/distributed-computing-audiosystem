import concurrent.futures
import random


class WorkerManager:
    def __init__(self, workers: list) -> None:
        self.workers = workers
        self.threadpool = concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.workers)
            )
        
    def submit_threadpool(self):
        for worker in self.workers:
            self.threadpool.submit(worker.loop)

    def stop_threadpool(self):
        for worker in self.workers:
            worker.stop()

    def add(self, worker) -> None:
        self.workers.append(worker)
        self.threadpool.submit(worker.loop)

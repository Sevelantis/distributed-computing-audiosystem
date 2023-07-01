import logging
import multiprocessing
import time


import torch

from src.utils import LogUtils
torch.set_num_threads(1) # load this to use 1 core instead of the whole CPU (very important)

from src.audio_worker.utils import SpawnerUtils


def workers_process(amount: int):
    from src.broker.factory import WorkerFactory
    from src.broker.manager import WorkerManager
    if amount == 0:
        return
    worker_manager = WorkerManager(
        workers=[
            WorkerFactory.create_audio_worker()
            for _ in range(amount)
        ]
    )
    worker_manager.submit_threadpool()
    logging.info(f'{amount} workers started listening for jobs.')
    while True:
        try:
            time.sleep(2.0)
        except KeyboardInterrupt as e:
            logging.info(e)
            break
    worker_manager.stop_threadpool()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger('stomp').setLevel(logging.ERROR)
logging.getLogger('uvicorn').setLevel(logging.ERROR)

def main():
    import src.config as config
    
    # healthy, unhealthy = SpawnerUtils.calc_workers_amount()
    unhealthy = config.WORKERS_UNHEALTHY
    healthy = config.WORKERS_HEALTHY
    
    unhealthy_process = multiprocessing.Process(target=workers_process, args=(unhealthy,))
    healthy_process = multiprocessing.Process(target=workers_process, args=(healthy,))
    
    unhealthy_process.start()
    healthy_process.start()
    
    start = time.time()
    killed = False
    while True:
        try:
            time.sleep(2.0)
            if not killed and (time.time() - start) > config.WORKER_SIMULATE_CRASH_AFTER and unhealthy != 0:
                logging.warning(f'Simulating workers crash. Killing {unhealthy} workers.')
                unhealthy_process.terminate()
                killed = True
        except KeyboardInterrupt as e:
            logging.info(e)
            break
    
    unhealthy_process.join()
    healthy_process.join()


if __name__ == '__main__':
    main()

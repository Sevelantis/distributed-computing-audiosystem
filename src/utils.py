
class IdManager:
    def __init__(self) -> None:
        self.music_id = 0
        self.job_id = 0
        self.track_id = 0
        
        
    def next_music_id(self) -> int:
        self.music_id += 1
        
        return self.music_id


    def next_job_id(self) -> int:
        self.job_id += 1
        
        return self.job_id
    
    
    def next_track_id(self) -> int:
        self.track_id += 1
        
        return self.track_id
    
    
    def reset(self) -> None:
        self.music_id = 0
        self.job_id = 0
        self.track_id = 0


import logging

class LogUtils():

    @classmethod
    def set_logging(cls):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logging.getLogger('stomp').setLevel(logging.ERROR)
        logging.getLogger('uvicorn').setLevel(logging.ERROR)
        
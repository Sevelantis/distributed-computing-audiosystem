import logging
import os
import shutil

from demucs.audio import save_audio
from torch import Tensor

import src.config as config


class Storage:
    def __init__(self) -> None:
        pass


    def save_bytes_audio_to_uri(
        self,
        data: bytes, 
        uri: str
        ) -> None:

        # create nested directories
        dir_path = os.path.dirname(uri)
        os.makedirs(dir_path, exist_ok=True)
        try:
            with open(uri, mode='bx') as f:
                f.write(data)
        except FileExistsError as e:
            logging.error(f'Error saving file "{uri}", it already exists!')


    def save_tensor_wav_to_uri(
        self,
        tensor: Tensor,
        uri: str,
        samplerate: int
        ) -> None:
        import os

        save_audio(tensor, uri, samplerate=samplerate)


    def reset(self) -> None:
        if os.path.exists(config.STORAGE_SERVER_DIR):
            shutil.rmtree(path=config.STORAGE_SERVER_DIR)
        os.makedirs(name=config.STORAGE_SERVER_DIR)
        logging.warn('Storage cleaned.')


    def clean_work_dir_tmp_files(self, work_dir: str) -> None:
        if os.path.exists(work_dir):
            files = os.listdir(work_dir)
            for file in files:
                if file.startswith('tmp'):
                    file_path = os.path.join(work_dir, file)
                    os.remove(file_path)

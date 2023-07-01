import logging
import time

import torch
from demucs.apply import BagOfModels, apply_model
from demucs.audio import AudioFile
from demucs.pretrained import get_model
from pydub import AudioSegment
from tinytag import TinyTag
from torch import Tensor

import src.config as config


class AudioUtils():


    DEMUCS_MODEL: BagOfModels = None


    @classmethod
    def retrieve_tensor_meta(cls, tensor: Tensor) -> dict:
        sample_rate = AudioUtils.get_model().samplerate
        dur = tensor.size(1) / sample_rate
        size = tensor.element_size() * tensor.numel()

        return {
            'duration': dur,
            'size': size
        }


    @classmethod
    def split_audio_to_chunks_from_uri(cls, uri: str) -> list[bytes]:
        song = AudioSegment.from_file(uri)
        song_len_ms = len(song)
        chunks = []
        chunk_time = -1
        if config.SPLIT_MODE == config.SPLIT_MODE_FIXED_JOBS:
            chunk_time = int(song_len_ms / (config.WORKERS_HEALTHY + config.WORKERS_UNHEALTHY)) + 1000
        elif config.SPLIT_MODE == config.SPLIT_MODE_FIXED_TIME:
            chunk_time = config.CHUNK_FIXED_TIME * 1000
        for i in range(0, int(song_len_ms / chunk_time + 1)):
            begin = i * chunk_time
            segment: AudioSegment = song[begin : begin + chunk_time]
            segment_bytes = segment.export(format=config.AUDIO_EXT_MP3).read()
            chunks.append(segment_bytes)

        return chunks


    @classmethod
    def merge_chunks_from_uris(cls, uris: list[str]) -> bytes:
        uris_sorted = sorted(uris)
        merge = AudioSegment.empty()
        for uri in uris_sorted:
            merge += AudioSegment.from_file(uri)

        return merge.export(format=config.AUDIO_EXT_MP3).read()


    @classmethod
    def split_wav_tensor(cls, wav: Tensor, N: int) -> list[Tensor]:
        
        return torch.tensor_split(input=wav, sections=N, dim=1)


    @classmethod
    def merge_mp3_byte_chunks(cls, chunks: list[bytes]) -> bytes:

        return torch.cat(tensors=chunks, dim=1)


    @classmethod
    def merge_wav_tensor_chunks(cls, chunks: list[Tensor]) -> Tensor:

        return torch.cat(tensors=chunks, dim=1)


    @classmethod
    def retrieve_audio_meta_from_uri(cls, uri: str) -> TinyTag:

        return TinyTag.get(filename=uri)


    @classmethod
    def get_model(cls) -> BagOfModels:
        if cls.DEMUCS_MODEL is None:
            cls.DEMUCS_MODEL: BagOfModels = get_model(name='htdemucs')
            cls.DEMUCS_MODEL.cpu()
            cls.DEMUCS_MODEL.eval()

        return cls.DEMUCS_MODEL


    @classmethod
    def mix_wavs_from_uris(cls, uris: list[str]) -> bytes:
        mix: AudioSegment = AudioSegment.from_file(uris[0])
        for uri in uris[1:]:
            audio: AudioSegment = AudioSegment.from_file(uri)
            mix = mix.overlay(audio, position=0)
        
        return mix.export(format=config.AUDIO_EXT_MP3).read()

    @classmethod
    def load_bytes_from_uri(cls, uri: str) -> bytes:
        with open(uri, 'rb') as file:
            wav_bytes = file.read()
        return wav_bytes


    @classmethod
    def separate_instruments_from_uri(
        cls,
        worker_id: int,
        uri: str,
        ) -> list[tuple[Tensor, str]]:
        '''This method produces a heavy wav tensor object.'''
        wav: Tensor = AudioFile(uri).read(
            streams=0,
            samplerate=cls.get_model().samplerate,
            channels=cls.get_model().audio_channels
            )
        ref = wav.mean(0)
        wav = (wav - ref.mean()) / ref.std()
        logging.debug(f'Worker[{worker_id}]: Start apply_model().')
        start = time.time()
        sources = apply_model(
            cls.get_model(),
            wav[None],
            device='cpu',
            # progress=True,
            num_workers=1
            )[0]
        logging.debug(f'Worker[{worker_id}]: Finish apply_model(), time: {time.time() - start}[s]')
        sources = sources * ref.std() + ref.mean()

        return zip(sources, cls.get_model().sources)


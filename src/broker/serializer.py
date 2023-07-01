import email
import pickle
from email.mime.audio import MIMEAudio
from email.mime.message import MIMEMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.system.job.message import JobDoneMsg, JobMsg
from src.system.message import WorkerResetMsg


class MessageSerializer:

    @classmethod
    def serialize_job_msg(cls, msg: JobMsg) -> str:
        mime_multipart = MIMEMultipart()
        # music_id
        part = MIMEText(str(msg.music_id))
        part.add_header('Content-ID', 'music_id')
        mime_multipart.attach(part)
        # job_id
        part = MIMEText(str(msg.job_id))
        part.add_header('Content-ID', 'job_id')
        mime_multipart.attach(part)
        # chunk
        pickled_chunk = pickle.dumps(msg.chunk)
        part = MIMEAudio(_audiodata=pickled_chunk, _subtype='mpeg')
        part.add_header('Content-ID', 'chunk')
        mime_multipart.attach(part)
        # chunk_nr
        part = MIMEText(str(msg.chunk_nr))
        part.add_header('Content-ID', 'chunk_nr')
        mime_multipart.attach(part)

        return mime_multipart.as_string()

    @classmethod
    def deserialize_job_msg(cls, serialized_msg: str) -> JobMsg:
        msg: JobMsg = JobMsg()
        mime_message: MIMEMessage = email.message_from_string(serialized_msg)
        for part in mime_message.walk():
            if part.get('Content-ID') == 'music_id':
                msg.music_id = int(part.get_payload(decode=True))
            elif part.get('Content-ID') == 'job_id':
                msg.job_id = int(part.get_payload(decode=True))
            elif part.get('Content-ID') == 'chunk':
                deserialized_chunk = part.get_payload(decode=True)
                msg.chunk = pickle.loads(deserialized_chunk)
            elif part.get('Content-ID') == 'chunk_nr':
                msg.chunk_nr = int(part.get_payload(decode=True))

        return msg

    @classmethod
    def serialize_job_done_msg(cls, msg: JobDoneMsg) -> str:
        mime_multipart = MIMEMultipart()
        # music_id
        part = MIMEText(str(msg.music_id))
        part.add_header('Content-ID', 'music_id')
        mime_multipart.attach(part)
        # job_id
        part = MIMEText(str(msg.job_id))
        part.add_header('Content-ID', 'job_id')
        mime_multipart.attach(part)
        # drums
        pickled_chunk = pickle.dumps(msg.drums)
        part = MIMEAudio(_audiodata=pickled_chunk, _subtype='mpeg')
        part.add_header('Content-ID', 'drums')
        mime_multipart.attach(part)
        # vocals
        pickled_chunk = pickle.dumps(msg.vocals)
        part = MIMEAudio(_audiodata=pickled_chunk, _subtype='mpeg')
        part.add_header('Content-ID', 'vocals')
        mime_multipart.attach(part)
        # other
        pickled_chunk = pickle.dumps(msg.other)
        part = MIMEAudio(_audiodata=pickled_chunk, _subtype='mpeg')
        part.add_header('Content-ID', 'other')
        mime_multipart.attach(part)
        # bass
        pickled_chunk = pickle.dumps(msg.bass)
        part = MIMEAudio(_audiodata=pickled_chunk, _subtype='mpeg')
        part.add_header('Content-ID', 'bass')
        mime_multipart.attach(part)
        # chunk_nr
        part = MIMEText(str(msg.chunk_nr))
        part.add_header('Content-ID', 'chunk_nr')
        mime_multipart.attach(part)
        # job_processing_time
        part = MIMEText(str(msg.job_processing_time))
        part.add_header('Content-ID', 'job_processing_time')
        mime_multipart.attach(part)

        return mime_multipart.as_string()

    @classmethod
    def deserialize_job_done_msg(cls, serialized_msg: str) -> JobDoneMsg:
        msg: JobDoneMsg = JobDoneMsg()
        mime_message: MIMEMessage = email.message_from_string(serialized_msg)
        for part in mime_message.walk():
            if part.get('Content-ID') == 'music_id':
                msg.music_id = int(part.get_payload(decode=True))
            elif part.get('Content-ID') == 'job_id':
                msg.job_id = int(part.get_payload(decode=True))
            elif part.get('Content-ID') == 'drums':
                deserialized_drums = part.get_payload(decode=True)
                msg.drums = pickle.loads(deserialized_drums)
            elif part.get('Content-ID') == 'vocals':
                deserialized_vocals = part.get_payload(decode=True)
                msg.vocals = pickle.loads(deserialized_vocals)
            elif part.get('Content-ID') == 'other':
                deserialized_other = part.get_payload(decode=True)
                msg.other = pickle.loads(deserialized_other)
            elif part.get('Content-ID') == 'bass':
                deserialized_bass = part.get_payload(decode=True)
                msg.bass = pickle.loads(deserialized_bass)
            elif part.get('Content-ID') == 'chunk_nr':
                msg.chunk_nr = int(part.get_payload(decode=True))
            elif part.get('Content-ID') == 'job_processing_time':
                msg.job_processing_time = float(part.get_payload(decode=True))

        return msg

    @classmethod
    def serialize_reset_msg(cls, msg: WorkerResetMsg) -> str:
        mime_multipart = MIMEMultipart()
        # worker_id
        part = MIMEText(msg.worker_id)
        part.add_header('Content-ID', 'worker_id')
        mime_multipart.attach(part)

        return mime_multipart.as_string()

    @classmethod
    def deserialize_worker_reset_msg(cls, serialized_msg: str) -> WorkerResetMsg:
        msg: AudioWorkerInfoMsg = WorkerResetMsg()
        mime_message: MIMEMessage = email.message_from_string(serialized_msg)
        for part in mime_message.walk():
            if part.get('Content-ID') == 'worker_id':
                msg.worker_id = part.get_payload(decode=False)

        return msg

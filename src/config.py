### User Conf ###
BROKER_HOST = 'localhost'           # broker IP
WORKERS_HEALTHY = 10                # Amount of workers that do not crash
WORKERS_UNHEALTHY = 2               # Amount of workers that crash (their process terminates)
WORKER_SIMULATE_CRASH_AFTER = 30    # After this amount of seconds.
### User Conf ###

APP_HOST='localhost'
APP_PORT=8888
BROKER_RESET_EXCHANGE = 'reset'


BACKEND_CORS_ORIGINS = [ "*" ]

# MESSAGE ACTIONS
ACTION_RESET_WORKER_MSG = 'RESET'
ACTION_JOB_MSG = 'JOB'
ACTION_JOB_DONE = 'JOB_DONE'
ACTION_WORKER_HEALTH_MSG = 'HEALTHCHECK'

# DEFAULTS
DEFAULT_URL = 'in_progress'
DEFAULT_TMP_SONG = 'in_progress'
DEFAULT_TMP_BAND = 'in_progress'
DEFAULT_TMP_PATH = 'in_progress'
DEFAULT_UNKNOWN_BAND = 'unknown_band'
DEFAULT_UNKNOWN_SONG = 'unknown_song'

# STORAGE
STORAGE_MODE_SUBMITTED = 'submitted'
STORAGE_MODE_PROCESSED = 'processed'
STORAGE_MODE_FINAL_MIX = 'final_mix'
STORAGE_MODE_SEPARATE = 'separated'
STORAGE_SERVER_DIR = 'storage_server'
STORAGE_WORKER_DIR = 'storage_worker'

# SPLIT MODE
SPLIT_MODE_FIXED_JOBS = 'fixed_jobs'
SPLIT_MODE_FIXED_TIME = 'fixed_time_mode'
SPLIT_MODE = SPLIT_MODE_FIXED_JOBS

# CHUNK
CHUNK_FIXED_TIME = 60

# WORKER
WORKER_THREAD_INTERVAL = 0.5
WORKER_NOT_RESPONDING_FOR_TOO_LONG_AFTER = 10
WORKER_GUARD_INTERVAL = 1.0
AUDIO_WORKER_CONN_HEARTBEATS = (15*1000, 15*1000) # (send_interval_ms, receive_interval_ms)

# AUDIO
AUDIO_INSTRUMENTS = ['drums', 'bass', 'other', 'vocals']
AUDIO_EXT_MP3 = 'mp3'
AUDIO_EXT_WAV = 'wav'

# BROKER CONNECTION
BROKER_PORT = 61613
BROKER_USERNAME = 'admin'
BROKER_PASSWORD = 'admin'

# WORKER DISCOVERY STATUS
WORKER_STATUS_ALIVE = 'ALIVE'
WORKER_STATUS_DEAD = 'DEAD'

# BROKER QUEUES
BROKER_JOB_QUEUE = 'BROKER_JOB_QUEUE'
BROKER_JOB_DONE_QUEUE = 'BROKER_JOB_DONE_QUEUE'

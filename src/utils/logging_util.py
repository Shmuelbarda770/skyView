import logging
import queue
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener

from src.utils.find_path_to_config import find_config

log_queue: queue.Queue = queue.Queue()

config_path: str = find_config()
config: ConfigParser = ConfigParser()
config.read(config_path)

log_file_name: str = config.get("logRotation", "FILENAME")
max_log_file_size: int = config.getint("logRotation", "MAX_LOG_FILE_SIZE")
max_backup_files: int = config.getint("logRotation", "BACKUP_COUNT")


rotating_file_handler: RotatingFileHandler = RotatingFileHandler(
    filename=log_file_name, maxBytes=max_log_file_size, backupCount=max_backup_files
)

rotating_file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

stream_handler: logging.StreamHandler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))


logger: logging.Logger = logging.getLogger()
logger.setLevel(logging.INFO)

queue_handler: QueueHandler = QueueHandler(log_queue)
logger.addHandler(queue_handler)


listener: QueueListener = QueueListener(log_queue, rotating_file_handler, stream_handler)
listener.start()

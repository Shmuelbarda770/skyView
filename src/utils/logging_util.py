import sys
import logging
import queue
from threading import Lock
from pathlib import Path
from configparser import ConfigParser

from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener

from src.utils.find_path_to_config import find_config

class LoggerManager:
    _instance = None
    _lock = Lock()
    _log_queue = queue.Queue()

    def __new__(cls):
        with cls._lock:

            if cls._instance is None:
                cls._instance = super(LoggerManager, cls).__new__(cls)
                cls._instance._initialize_logger()
            return cls._instance


    @classmethod
    def _initialize_logger(cls):
        try:
            config_path = find_config()
            config = ConfigParser()
            config.read(config_path)

            log_file_name = config.get('logRotation', 'FILENAME')
            max_log_file_size = config.getint('logRotation', 'MAX_LOG_FILE_SIZE')
            max_backup_files = config.getint('logRotation', 'BACKUP_COUNT')


            rotating_file_handler = RotatingFileHandler(
                filename=log_file_name,
                maxBytes=max_log_file_size,
                backupCount=max_backup_files 
            )

            rotating_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            
            cls.logger = logging.getLogger()
            cls.logger.setLevel(logging.INFO)

            queue_handler = QueueHandler(cls._log_queue)
            cls.logger.addHandler(queue_handler)

            
            cls.listener = QueueListener(cls._log_queue, rotating_file_handler, stream_handler)
            cls.listener.start()

        except Exception as e:
            pass
            

    def get_logger(self):
        return self.logger

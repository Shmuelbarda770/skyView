
import logging
from logging.handlers import TimedRotatingFileHandler, QueueHandler, QueueListener
import queue
from configparser import ConfigParser
from threading import Lock 
import sys
from pathlib import Path

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
    def _find_config(cls):
        if hasattr(sys, "_MEIPASS"):
            PROJ_ROOT = Path(getattr(sys, "_MEIPASS"))
        else:
            PROJ_ROOT = Path(r'C:\Users\A\skyView')
            

        return PROJ_ROOT / 'config.ini'
    
    @classmethod
    def _initialize_logger(cls):
        try:
            config_path = cls._find_config()
            print(config_path)
            config = ConfigParser()
            config.read(config_path)

            log_file_name = config.get('logRotation', 'FILENAME')
            log_rotation_time = config.get('logRotation', 'WHEN')
            log_rotation_interval = config.getint('logRotation', 'INTERVAL')
            max_backup_files = config.getint('logRotation', 'BACKUP_COUNT')

            rotating_handler = TimedRotatingFileHandler(
                filename=log_file_name,
                when=log_rotation_time,
                interval=log_rotation_interval,
                backupCount=max_backup_files
            )
            rotating_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            
            cls.logger = logging.getLogger()
            cls.logger.setLevel(logging.INFO)

            queue_handler = QueueHandler(cls._log_queue)
            cls.logger.addHandler(queue_handler)

            
            cls.listener = QueueListener(cls._log_queue, rotating_handler, stream_handler)
            cls.listener.start()

        except Exception as e:
            print(f"Error initializing logger: {e}")
            raise

    def get_logger(self):
        return self.logger

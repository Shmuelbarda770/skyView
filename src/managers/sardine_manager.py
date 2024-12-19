import threading
import queue
from queue import Queue
from logging import Logger
from configparser import ConfigParser

from src.GUI.global_variables import global_variables_state
from src.consumer.sardine_consumer import SardineConsumer
from src.publisher.gcp_publisher.cloud_data_sender import CloudDataSender
from src.models.message_id_generator import MessageIDGenerator
from src.models.class_config.config import Config
from src.utils.logging_util import LoggerManager
from src.utils.find_path_to_config import find_config

class SardineManager:
    def __init__(self,config:Config):

        # config_path:str = find_config()
        # config:ConfigParser = ConfigParser()
        # config.read(config_path)


        # self.QUEUE_SIZE:int = config.getint('settings', 'QUEUE_SIZE')
        
        self.config:Config=config
        self.data_queue:Queue=queue.Queue(maxsize=15)
        self.is_connection_active_flag:threading.Event=threading.Event()
        self.message_id_generator:MessageIDGenerator =MessageIDGenerator()
        ## TODO: make logger shared not using dict, maybe import the file directly
        self.logger:Logger=global_variables_state["logger"].get_logger()


    def start_listening_for_sardine(self):
        try:
            self.is_connection_active_flag.set()
            
            sardine_consumer :SardineConsumer= SardineConsumer(self.data_queue, self.is_connection_active_flag,self.config)
            cloud_data_sender:CloudDataSender=CloudDataSender(self.data_queue, self.message_id_generator, self.is_connection_active_flag,self.config)
            
            thread_socket_manager: threading.Thread = threading.Thread(target=sardine_consumer.run, daemon=True)
            thread_cloud_data_sender: threading.Thread =  threading.Thread(target=cloud_data_sender.send_data_to_cloud, daemon=True)
            
            thread_socket_manager.start()
            thread_cloud_data_sender.start()

            thread_socket_manager.join()
            thread_cloud_data_sender.join()

        except Exception as e:
            self.logger.error(f"Error in thread: {e}")
        finally:
            self.logger.info("Thread shut down")
            self.logger.info(f"now enumerating threads is:{len(threading.enumerate())}")


    def stop_listening_for_sardine(self):
        self.logger.info("Stopping threads.")
        self.is_connection_active_flag.clear()
        while not self.data_queue.empty():
            self.data_queue.get()
        self.logger.info("Threads stopped.")


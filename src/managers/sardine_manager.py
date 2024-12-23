import threading
import queue
from queue import Queue
from logging import Logger
import configparser

from src.GUI.global_variables import global_variables_state
from src.consumer.sardine_consumer import SardineConsumer
from src.publisher.gcp_publisher.cloud_data_sender import CloudDataSender
from src.models.message_id_generator import MessageIDGenerator
from src.models.class_config.config_data import ConfigData


class SardineManager:
    def __init__(self, config_data: ConfigData):

        self.config: configparser.ConfigParser = global_variables_state["config"]
        self.QUEUE_SIZE: int = self.config.getint("settings", "QUEUE_SIZE")

        self.config_data: ConfigData = config_data
        self.data_queue: Queue = queue.Queue(maxsize=self.QUEUE_SIZE)
        
        self.is_connection_active_flag: threading.Event = threading.Event()
        self.message_id_generator: MessageIDGenerator = MessageIDGenerator()
        self.logger: Logger = global_variables_state["logger"]

    def start_listening_for_sardine(self):
        try:
            self.is_connection_active_flag.set()

            sardine_consumer: SardineConsumer = SardineConsumer(
                self.data_queue, self.is_connection_active_flag, self.config_data
            )
            cloud_data_sender: CloudDataSender = CloudDataSender(
                self.data_queue, self.message_id_generator, self.is_connection_active_flag, self.config_data
            )

            thread_socket_manager: threading.Thread = threading.Thread(target=sardine_consumer.run, daemon=True)
            thread_cloud_data_sender: threading.Thread = threading.Thread(
                target=cloud_data_sender.send_data_to_cloud, daemon=True
            )

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

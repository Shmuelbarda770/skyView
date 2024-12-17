import threading
import queue
from queue import Queue
from logging import Logger
from src.consumer.sardine_consumer import SardineConsumer
from src.publisher.gcp_publisher.cloud_data_sender import CloudDataSender
from src.GUI.global_variables import global_variables_state
from src.models.message_id_generator import MessageIDGenerator

class SardineManager:
    ##2.TODO: add type hints (maybe pass a config parameter)
    def __init__(self,**kwargs):
        
        self.kwargs=kwargs

        self.logger:Logger=global_variables_state["logger"].get_logger()
        self.data_queue:Queue=queue.Queue()
        self.is_sardine_connection_active_flag:threading.Event=threading.Event()
        self.message_id_generator=MessageIDGenerator()
        

    def start_listening_for_sardine(self):
        try:
            self.is_sardine_connection_active_flag.set()
            socket_manager :SardineConsumer= SardineConsumer(self.data_queue, self.is_sardine_connection_active_flag,**self.kwargs)
            cloud_data_sender:CloudDataSender=CloudDataSender(self.data_queue, self.message_id_generator, self.is_sardine_connection_active_flag,**self.kwargs)
            
            tread_socket_manager: threading.Thread = threading.Thread(target=socket_manager.run, daemon=True)
            tread_cloud_data_sender: threading.Thread =  threading.Thread(target=cloud_data_sender.send_data_to_cloud, daemon=True)
            
            tread_socket_manager.start()
            tread_cloud_data_sender.start()

            tread_socket_manager.join()
            tread_cloud_data_sender.join()

        except Exception as e:
            self.logger.error(f"Error in thread: {e}")
        finally:
            self.logger.info("Thread shut down")

            print(f"Active threads: {len(threading.enumerate())}")


    def stop_listening_for_sardine(self):
        self.logger.info("Stopping threads.")
        self.is_sardine_connection_active_flag.clear()
        while not self.data_queue.empty():
            self.data_queue.get()
        self.logger.info("Threads stopped.")


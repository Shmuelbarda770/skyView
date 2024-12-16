import threading
import queue
from queue import Queue

from src.consumer.sardine_consumer import SardineConsumer
from src.publisher.gcp_publisher.cloud_data_sender import CloudDataSender
from src.GUI.global_variables import global_variables_state

class SardineManager:
    ##2.TODO: add type hints (maybe pass a config parameter)
    def __init__(self, route_id,platform_flight_index,platform_id, platform_name, date,
                 update_connection_status_message,
                 show_error_in_screen,update_traffic_light_status,
                 increment_received_json_counter,increment_send_json_counter,update_ui_when_send_data):
        
        self.logger=global_variables_state["logger"].get_logger()
        ##2.TODO: pass this parameter inside the threads

        self.data_queue:Queue=queue.Queue()
        self.is_sardine_connection_active_flag=threading.Event()

        self.increment_received_json_counter=increment_received_json_counter
        self.update_ui_when_send_data=update_ui_when_send_data
        self.increment_send_json_counter=increment_send_json_counter
        self.route_id = route_id
        self.platform_flight_index = platform_flight_index
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.date = date
        self.update_connection_status_message = update_connection_status_message
        self.show_error_in_screen = show_error_in_screen
        self.update_traffic_light_status=update_traffic_light_status
        

    def start_listening_for_sardine(self):
        try:
            socket_manager :SardineConsumer= SardineConsumer(self.route_id, self.platform_flight_index, self.platform_id,
                                          self.platform_name, self.date,
                                          self.update_connection_status_message,
                                          self.show_error_in_screen,self.update_traffic_light_status,
                                          self.increment_received_json_counter,self.data_queue,self.is_sardine_connection_active_flag)
            cloud_data_sender:CloudDataSender=CloudDataSender(self.show_error_in_screen,
                                              self.update_ui_when_send_data,self.data_queue,self.is_sardine_connection_active_flag)
            
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
        self.connection_status_flag.clear()
        while not self.data_queue.empty():
            self.data_queue.get()
        self.logger.info("Threads stopped.")


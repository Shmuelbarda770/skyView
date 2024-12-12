import threading
from src.sardine_lisener.socket_controller import SocketController
from src.GCP_publisher.cloud_data_sender import CloudDataSender
from src.app_gui.global_variables import global_variables_state
from queue import Queue

class SocketThreadManager:
    def __init__(self, route_id,platform_flight_index,platform_id, platform_name,date,
                 status_indicator_unconnected,status_indicator_connected_and_receives_data,status_indicator_send_to_cloud ,status_connection,
                 received_json_counter,sent_json_counter,show_running_error,page,update_traffic_light_status,
                 increment_received_json_counter,increment_send_json_counter):
        
        self.connection_status_flag=global_variables_state["connection_status_flag"]
        self.data_queue:Queue=global_variables_state["data_queue"]
        self.logger=global_variables_state["logger"].get_logger()
        self.increment_received_json_counter=increment_received_json_counter
        self.increment_send_json_counter=increment_send_json_counter
        self.route_id = route_id
        self.platform_flight_index = platform_flight_index
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.date = date
        self.status_indicator_unconnected = status_indicator_unconnected
        self.status_indicator_connected_and_receives_data = status_indicator_connected_and_receives_data
        self.status_indicator_send_to_cloud = status_indicator_send_to_cloud
        self.status_connection = status_connection
        self.received_json_counter = received_json_counter
        self.sent_json_counter = sent_json_counter
        self.show_running_error = show_running_error
        self.update_traffic_light_status=update_traffic_light_status
        self.page=page
        



    def start_thread(self, target, args=None):
        thread = threading.Thread(target=target, args=args, daemon=True)
        thread.start()
        return thread

    def open_socket_running(self):
        try:
            socket_manager = SocketController(self.route_id, self.platform_flight_index, self.platform_id,
                                          self.platform_name, self.date, self.status_indicator_unconnected,
                                          self.status_indicator_connected_and_receives_data, self.status_indicator_send_to_cloud,
                                          self.status_connection, self.received_json_counter,
                                          self.sent_json_counter, self.show_running_error,self.update_traffic_light_status,
                                          self.increment_received_json_counter) 
            cloud_data_sender=CloudDataSender(self.show_running_error,
                                              self.update_traffic_light_status,
                                              self.increment_send_json_counter)
            
            tread_socket_manager = self.start_thread(socket_manager.run())
            tread_cloud_data_sender = self.start_thread(cloud_data_sender.send_data_to_cloud())

            tread_socket_manager.join()
            tread_cloud_data_sender.join()

        except Exception as e:
            self.logger.error(f"Error in thread: {e}")
        finally:
            self.logger.info("Thread shut down")
            print(f"Active threads: {len(threading.enumerate())}")


    def stop_socket_running(self):
        self.logger.info("Stopping threads.")
        self.connection_status_flag.clear()
        while not self.data_queue.empty():
            self.data_queue.get()
        self.logger.info("Threads stopped.")
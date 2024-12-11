import threading
from src.sardine_lisener.socket_controller import SocketController
from src.GCP_publisher.cloud_data_sender import CloudDataSender
from src.app_gui.global_variables import global_variables_state


class SocketThreadManager:
    def __init__(self, route_id, platform_flight_index, platform_id, platform_name, date,
                 status_indicator_red, status_indicator_yellow, status_indicator_green, status_connection,
                 cont_json_received, cont_send_json_to_cloud, running_problems):
        self.connection_status_flag=global_variables_state["connection_status_flag"]
        self.route_id = route_id
        self.platform_flight_index = platform_flight_index
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.date = date
        self.status_indicator_red = status_indicator_red
        self.status_indicator_yellow = status_indicator_yellow
        self.status_indicator_green = status_indicator_green
        self.status_connection = status_connection
        self.cont_json_received = cont_json_received
        self.cont_send_json_to_cloud = cont_send_json_to_cloud
        self.running_problems = running_problems
        self.logger=global_variables_state["logger"]

    def start_thread(self, target, args=None):
        thread = threading.Thread(target=target, args=args, daemon=True)
        thread.start()
        return thread

    def open_socket(self):
        try:
            socket_manager = SocketController(self.route_id, self.platform_flight_index, self.platform_id,
                                          self.platform_name, self.date, self.status_indicator_red,
                                          self.status_indicator_yellow, self.status_indicator_green,
                                          self.status_connection, self.cont_json_received,
                                          self.cont_send_json_to_cloud, self.running_problems)
            cloud_data_sender=CloudDataSender(self.status_indicator_green,self.status_indicator_red,self.status_indicator_yellow, self.running_problems)
            
            tread_socket_manager = self.start_thread(socket_manager.run)
            tread_cloud_data_sender = self.start_thread(cloud_data_sender.send_data_to_cloud())

            tread_socket_manager.join()
            tread_cloud_data_sender.join()

        except Exception as e:
            self.logger.error(f"Error in thread: {e}")
        finally:
            self.logger.info("Thread shut down")
            print(f"Active threads: {len(threading.enumerate())}")
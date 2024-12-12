import queue
from src.GCP_publisher.json_sender import send

from src.app_gui.global_variables import global_variables_state

class CloudDataSender():
    def __init__(self, show_running_error,update_traffic_light_status,increment_send_json_counter):
        
        self.logger = global_variables_state["logger"].get_logger()
        self.data_queue=global_variables_state["data_queue"]
        self.connection_status_flag=global_variables_state["connection_status_flag"]
        self.show_running_error=show_running_error
        self.update_traffic_light_status=update_traffic_light_status
        self.increment_send_json_counter=increment_send_json_counter
        
    def send_data_to_cloud(self):
        while self.connection_status_flag.is_set():
            try:
                data_from_drone = self.data_queue.get(block=True, timeout=1)
                if data_from_drone:
                    send(data_from_drone)
                    self.logger.info("Sending data to cloud")
                    self.update_traffic_light_status("green")
                    self.increment_send_json_counter()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error sending data: {e}")
                self.show_running_error("Error sending data")
                if not self.connection_status_flag.is_set():
                    break

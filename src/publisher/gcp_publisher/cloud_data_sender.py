import queue

from src.publisher.gcp_publisher.json_sender import send
from src.GUI.global_variables import global_variables_state

class CloudDataSender():
    def __init__(self, show_error_in_screen,update_ui_when_send_data,data_queue,is_sardine_connection_active_flag):
        
        self.logger = global_variables_state["logger"].get_logger()
        self.data_queue: queue.Queue =data_queue
        self.is_sardine_connection_active_flag= is_sardine_connection_active_flag
        
        self.show_error_in_screen = show_error_in_screen
        self.update_ui_when_send_data = update_ui_when_send_data
        
    def send_data_to_cloud(self):
        while self.sardine_connection_active_flag():
            try:
                data_from_drone = self.data_queue.get(block=True, timeout=1)
                if data_from_drone:
                    print(data_from_drone)
                    send(data_from_drone)
                    self.logger.info("Sending data to cloud")
                    self.update_ui_when_send_data()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error sending data: {e}")
                self.show_error_in_screen("Error sending data")
                if not self.connection_status_flag.is_set():
                    break

    def sardine_connection_active_flag(self):
        return  self.is_sardine_connection_active_flag.is_set()


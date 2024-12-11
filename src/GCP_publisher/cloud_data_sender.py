import queue
from src.GCP_publisher.json_sender import send
from utils.logging_util import LoggerManager
from app_gui.global_variables import global_variables_state

class CloudDataSender():
    def __init__(self):
        self.logger = LoggerManager.get_logger()
        self.data_queue=global_variables_state["data_queue"]
        self.connection_status_flag=global_variables_state["connection_status_flag"]

    def send_data_to_cloud(self, status_indicator_green, status_indicator_red, status_indicator_yellow, json_send_count, running_problems):
        while self.connection_status_flag.is_set():
            try:
                data_from_drone = self.data_queue.get(block=True, timeout=1)
                if data_from_drone:
                    send(data_from_drone)
                    self.logger.info("Sending data to cloud")
                    color_status = "green"
                    self.light(status_indicator_green, status_indicator_red, status_indicator_yellow, color_status)
                    json_send_count += 1
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error sending data: {e}")
                self.show_error_in_screen(running_problems, "Error sending data")
                if not self.connection_status_flag.is_set():
                    break

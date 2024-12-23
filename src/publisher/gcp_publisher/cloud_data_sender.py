import queue
from logging import Logger
import threading
import json
import time

from src.publisher.gcp_publisher.json_sender import send
from src.GUI.global_variables import global_variables_state
from src.models.class_config.config_data import ConfigData
from src.models.message_id_generator import MessageIDGenerator
from src.models.flight_data import FlightData


class CloudDataSender:
    def __init__(
        self,
        data_queue: queue.Queue,
        message_id_generator: MessageIDGenerator,
        is_connection_active_flag: threading.Event,
        config_data: ConfigData,
    ):

        self.config_data: ConfigData = config_data
        self.logger: Logger = global_variables_state["logger"]
        self.data_queue: queue.Queue = data_queue
        self.is_connection_active_flag: threading.Event = is_connection_active_flag
        self.message_id_generator: MessageIDGenerator = message_id_generator

    def send_data_to_cloud(self) -> None:
        while self.connection_active_flag():
            try:
                self.logger.info("Waiting to receive data from the queue")
                data_from_drone: FlightData = self.data_queue.get(block=True, timeout=1)

                if data_from_drone:
                    convert_object_to_json = self.convert_and_add_messageid_to_json(data_from_drone)

                    self.logger.info(f"data is : {convert_object_to_json}")
                    start_time = time.time()
                    send(convert_object_to_json)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    self.logger.info(f"time og running function send is {execution_time}")

                    self.logger.info("Sending data to cloud")
                    self.config_data.update_ui_when_send_data()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error sending data: {e}")
                self.config_data.show_error_in_screen("Error sending data")
                if not self.connection_active_flag():
                    break

    def connection_active_flag(self):
        return self.is_connection_active_flag.is_set()

    def convert_and_add_messageid_to_json(self, data_from_drone: FlightData):
        convert_object_to_str: str = data_from_drone.model_dump_json()
        convert_object_to_json:dict = json.loads(convert_object_to_str)
        convert_object_to_json["MESSAGEID"] = self.message_id_generator.get_next_id()
        return convert_object_to_json

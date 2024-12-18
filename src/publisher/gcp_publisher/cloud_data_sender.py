import queue
from logging import Logger
import threading
import json

from src.publisher.gcp_publisher.json_sender import send
from src.GUI.global_variables import global_variables_state
from src.models.class_config.sardine_config import SardineConfig
from src.models.message_id_generator import MessageIDGenerator
from src.models.flight_data import FlightData


class CloudDataSender():
    def __init__(self,data_queue: queue.Queue,message_id_generator:MessageIDGenerator,
                 is_sardine_connection_active_flag:threading.Thread,sardine_config:SardineConfig):
        ##TODO: should not get sardine config
        self.sardine_config:SardineConfig=sardine_config
        self.logger:Logger = global_variables_state["logger"].get_logger()
        self.data_queue: queue.Queue =data_queue
        self.is_sardine_connection_active_flag:threading.Thread =is_sardine_connection_active_flag
        self.message_id_generator:MessageIDGenerator=message_id_generator
        
    def send_data_to_cloud(self)->None:
        ## TODO: sardine_connection_active_flag should no include sardine in the name
        while self.sardine_connection_active_flag():
            try:

                data_from_drone:FlightData = self.data_queue.get(block=True, timeout=1)
                
                if data_from_drone:
                    convert_object_to_json=self.convert_and_add_messageid_to_json(data_from_drone)
                    print(convert_object_to_json)
                    send(convert_object_to_json)
                    self.logger.info("Sending data to cloud")
                    self.sardine_config.update_ui_when_send_data()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error sending data: {e}")
                self.sardine_config.show_error_in_screen("Error sending data")
                if not self.sardine_connection_active_flag():
                    break

    def sardine_connection_active_flag(self):
        return  self.is_sardine_connection_active_flag.is_set()
    
    def convert_and_add_messageid_to_json(self,data_from_drone:FlightData):
        convert_object_to_json:FlightData=data_from_drone.model_dump_json()
        convert_object_to_json = json.loads(convert_object_to_json)
        convert_object_to_json["MESSAGEID"]=self.message_id_generator.get_next_id()
        return convert_object_to_json


import queue
from logging import Logger

from src.publisher.gcp_publisher.json_sender import send
from src.GUI.global_variables import global_variables_state


class CloudDataSender():
    def __init__(self,message_id_generator,data_queue,is_sardine_connection_active_flag,**kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value) 
        
        self.logger:Logger = global_variables_state["logger"].get_logger()
        self.data_queue: queue.Queue =data_queue
        self.is_sardine_connection_active_flag: queue.Queue =is_sardine_connection_active_flag
        self.message_id_generator=message_id_generator
        
    def send_data_to_cloud(self):
        while self.sardine_connection_active_flag():
            try:
                data_from_drone = self.data_queue.get(block=True, timeout=1)
                
                if convert_object_to_json:
                    convert_object_to_json=self.convert_and_add_messageid_to_json(data_from_drone)
                    print(convert_object_to_json)
                    send(convert_object_to_json)
                    self.logger.info("Sending data to cloud")
                    self.update_ui_when_send_data()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error sending data: {e}")
                self.show_error_in_screen("Error sending data")
                if not self.is_sardine_connection_active_flag.is_set():
                    break

    def sardine_connection_active_flag(self):
        return  self.is_sardine_connection_active_flag.is_set()
    
    def convert_and_add_messageid_to_json(self,data_from_drone):
        convert_object_to_json=data_from_drone.json()
        convert_object_to_json["MESSAGEID"]=self.message_id_generator.get_next_id()
        return convert_object_to_json


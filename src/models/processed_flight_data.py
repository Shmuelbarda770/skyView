import datetime
import logging
from queue import Queue

from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Optional,Callable,ClassVar

from src.app_gui.global_variables import global_variables_state
from src.models.message_id_generator import MessageIDGenerator

class ProcessedFlightData(BaseModel):
    route_id: str
    platform_name: str
    platform_id: int
    date: str
    platform_flight_index: int
    show_error_in_screen: Optional[Callable] = None

    message_id_counter: int = 0
    id_for_MessageID: ClassVar[MessageIDGenerator] = MessageIDGenerator()
    data_queue :Queue = global_variables_state["data_queue"]
    logger:logging.Logger = global_variables_state["logger"]

    class Config:
        arbitrary_types_allowed = True


    @classmethod
    def validate_time_of_last_known_location(cls, value: str) -> str:
        if len(value) < 20 or len(value) > 30:
            raise ValueError("Invalid timeOfLastKnownLocation length. It should be between 20 and 30")
        return value

    @classmethod
    def validate_coordinate(cls, value):
        if len(value) != 2:
            raise ValueError("Invalid coordinate length. It should be dict and the length should be 2")
        
        latitude = value['latitude']
        longitude = value['longitude']

        if not (10 <= latitude <= 50):
            raise ValueError("Latitude out of range. It should be between 10 and 50")
        
        if not (10 <= longitude <= 50):
            raise ValueError("Longitude out of range. It should be between 10 and 50")
        
        return value

    @classmethod
    def validate_height(cls, value: float) -> float:
        if value < 0 or value > 5000:
            raise ValueError("Height out of range. It should be between 0 and 5000")
        return value

    @classmethod
    def validate_azimuth(cls, value: float) -> float:
        if value < 0 or value > 360:
            raise ValueError("Azimuth out of range. It should be between 0 and 360")
        return value

    # @classmethod
    # def validate_roll(cls, value: float) -> float:
    #     if value < -181 or value > 181:
    #         raise ValueError("")
    #     return value

    # @classmethod
    # def validate_pitch(cls, value: float) -> float:
    #     if value < -181 or value > 181:
    #         raise ValueError("")
    #     return value
    
    def validate_drone_data (self, azimuth: float, coordinate: list, height: float, timeOfLastKnownLocation: str):
        try:
            if all([
                self.validate_azimuth(azimuth),
                self.validate_height(height),
                self.validate_coordinate(coordinate),
                self.validate_time_of_last_known_location(timeOfLastKnownLocation)
            ]):
                return True
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")


    def process_flight_data(self, azimuth: float,coordinate: list,height: float,timeOfLastKnownLocation: str,droneId: int):

        if not self.validate_drone_data(azimuth,coordinate,height,timeOfLastKnownLocation):
            return
            
        try:
            flight_id:str = self._generate_flight_id(self.platform_name, self.platform_id, self.date, self.platform_flight_index)
            message_id:int = self.id_for_MessageID.get_next_id()

            processed_data :dict = {
                "AZIMUTH": self.round_to_decimal_places(azimuth, 2),
                "COORDINATE": {
                    "latitude": self.round_to_decimal_places(coordinate[0], 7),
                    "longitude": self.round_to_decimal_places(coordinate[1], 7)
                },
                "DATE": self.date,
                "Platform_Flight_Index": int(self.platform_flight_index),
                "FLIGHT_ID": flight_id,
                "HEIGHT": self.round_to_decimal_places(height, 1),
                "MESSAGEID": message_id,
                "PITCH": 0.0,
                "PLATFORMID": self.platform_id,
                "PLATFORMNAME": self.platform_name,
                "ROLL": 0.0,
                "ROUTEID": self.route_id,
                "TIMEOFLASTKNOWNLOCATION": timeOfLastKnownLocation
            }
            self.add_json_to_queue(processed_data)

        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            self.show_error_in_screen(f"Validation error: {e}")

        except Exception as e:
            self.logger.error(f"Error processing flight data: {e}")
            self.show_error_in_screen(f"Error processing flight data: {e}")
            

    @staticmethod
    def round_to_decimal_places(number_to_float: float, decimal_places:int)->float:
        return round(number_to_float, decimal_places)


    def _generate_flight_id(self, platform_name, platform_id, date, platform_flight_index)-> str:
        conversion_date_for_flight_id:str = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
        return f"{platform_name}{platform_id}_{conversion_date_for_flight_id}_{str(platform_flight_index).zfill(4)}"


    def clear_queue(self):
        while not self.data_queue.empty():
            try:
                self.data_queue.get_nowait()
            except Exception as e:
                self.logger.error(f"Failed to clear the queue: {e}")
            
        self.logger.info("Queue has been cleared")


    def add_json_to_queue(self,data_to_queue: dict):
        if self.data_queue.full():
            self.clear_queue()
                        
        self.data_queue.put(data_to_queue)
        self.logger.info("Data added to queue")
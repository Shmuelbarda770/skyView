from pydantic import BaseModel,ValidationError
import json
import datetime
from src.models.message_ID_generator import MessageIDGenerator
from src.models.incoming_data import IncomingData
from src.app_gui.global_variables import global_variables_state
from queue import Queue
import logging

class ProcessedData(BaseModel):
    AZIMUTH: float
    COORDINATE: dict
    DATE: str
    Platform_Flight_Index: int
    FLIGHT_ID: str
    HEIGHT: float
    MESSAGEID: int
    PITCH: float
    PLATFORMID: int
    PLATFORMNAME: str
    ROLL: float
    ROUTEID: int
    TIMEOFLASTKNOWNLOCATION: str



class FlightDataProcessor:
    def __init__(self):
        self.MessageIDGenerator=MessageIDGenerator()
        self.logger:logging.Logger = global_variables_state["logger"].get_logger()
        self.data_queue: Queue=global_variables_state["data_queue"]

    def process_flight_data(self, new_json, route_id, platform_name, platform_id, 
                            date , platform_flight_index):
    
        try:
            incoming_data = self._parse_incoming_data(new_json)
            if not incoming_data:
                return

            flight_id = self._generate_flight_id(platform_name, platform_id, date, platform_flight_index)
            message_id = self.MessageIDGenerator.get_next_id()

            
            processed_data = ProcessedData(
                AZIMUTH=self.round_to_decimal_places(incoming_data.azimuth, 2),
                COORDINATE={
                    "latitude":self.round_to_decimal_places(incoming_data.coordinate[0], 7),
                    "longitude":self.round_to_decimal_places(incoming_data.coordinate[1], 7)},
                DATE=date,
                Platform_Flight_Index=int(platform_flight_index),
                FLIGHT_ID=flight_id,
                HEIGHT=self.round_to_decimal_places(incoming_data.height,1),
                MESSAGEID=message_id,
                PITCH=0.0, 
                PLATFORMID=int(platform_id),
                PLATFORMNAME=platform_name,
                ROLL=0.0,
                ROUTEID=route_id,
                TIMEOFLASTKNOWNLOCATION=incoming_data.timeOfLastKnownLocation
            )
            self.data_queue.put(processed_data) 

        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            return None

        except Exception as e:
            self.logger.error(f"Error processing flight data: {e}")
            return None

    def _parse_incoming_data(self, new_json):
        try:
            # data_conversion = json.loads(new_json)
            # return IncomingData(**data_conversion)
            return IncomingData(**new_json)
        except Exception as e:
            self.logger.error(f"Error incoming data: {e}")
            return False

    def _generate_flight_id(self, platform_name, platform_id, date, platform_flight_index):

        conversion_date_for_flight_id = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
        return f"{platform_name}{platform_id}_{conversion_date_for_flight_id}_{str(platform_flight_index).zfill(4)}"

    
    def round_to_decimal_places(value, decimal_places):
        return round(value, decimal_places)

new_json ={'azimuth': 0.0, 'coordinate': {'latitude': 0, 'longitude': 0},  'height': 0, 'timeOfLastKnownLocation': '2024-12-09 11:36:55.161440'}
route_id='ffghghfsfh'
platform_name='SDA'
platform_id=232
date='2024-12-09'
platform_flight_index=1234

x=FlightDataProcessor().process_flight_data(new_json, route_id, platform_name, platform_id, 
                            date, platform_flight_index)
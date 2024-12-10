from pydantic import BaseModel,ValidationError
import json
from src.models.incoming_data import IncomingData
import datetime

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


def process_flight_data(
new_json: json, 
route_id: str, 
platform_name: str, 
platform_id: int, 
date: str, 
platform_flight_index: int, 
running_problems,
logger
) -> ProcessedData:
    try:
        id_for_message_id = id_for_MessageID_obj.get_next_id()

       
        data_conversion = json.loads(new_json)
        incoming_data = IncomingData(**data_conversion)

        
        conversion_date_for_flight_id = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')

       
        processed_data = ProcessedData(
            AZIMUTH=round(incoming_data.azimuth, 2),
            COORDINATE={
                "latitude": round(incoming_data.coordinate[0], 7),
                "longitude": round(incoming_data.coordinate[1], 7)
            },
            DATE=date,
            Platform_Flight_Index=int(platform_flight_index),
            FLIGHT_ID=f"{platform_name}{platform_id}_{conversion_date_for_flight_id}_{str(platform_flight_index).zfill(4)}",
            HEIGHT=round(incoming_data.height, 1),
            MESSAGEID=id_for_message_id,
            PITCH=0.00,
            PLATFORMID=int(platform_id),
            PLATFORMNAME=platform_name,
            ROLL=0.00,
            ROUTEID=route_id,
            TIMEOFLASTKNOWNLOCATION=incoming_data.timeOfLastKnownLocation
        )
        return processed_data
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        
        return None

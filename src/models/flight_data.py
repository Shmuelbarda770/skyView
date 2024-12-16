import datetime
import logging

from pydantic import BaseModel, ValidationError,field_validator
from typing import Optional,Callable,ClassVar

from src.GUI.global_variables import global_variables_state


##2.TODO: this should be only a model (hold data and validation). 
##2.TODO: need to change the name of the object
class FlightData(BaseModel):
    ROUTEID:str
    PLATFORMNAME: str
    FLIGHT_ID: int
    DATE: str
    Platform_Flight_Index: int
    AZIMUTH: float
    COORDINATE: list
    HEIGHT: float
    TIMEOFLASTKNOWNLOCATION: str
    ROLL:float
    PITCH:float
    MESSAGEID:int
    PLATFORMID:int


    # logger:logging.Logger = global_variables_state["logger"]

    class Config:
        arbitrary_types_allowed = True

    @field_validator("TIMEOFLASTKNOWNLOCATION")
    @classmethod
    def validate_time_of_last_known_location(cls, value: str) -> str:
        if len(value) < 20 or len(value) > 30:
            raise ValueError("Invalid timeOfLastKnownLocation length. It should be between 20 and 30")
            
        return value

    @field_validator("COORDINATE")
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

    @field_validator("HEIGHT")
    @classmethod
    def validate_height(cls, value: float) -> float:
        if value < 0 or value > 5000:
            raise ValueError("Height out of range. It should be between 0 and 5000")
        return value

    @field_validator("AZIMUTH")
    @classmethod
    def validate_azimuth(cls, value: float) -> float:
        if value < 0 or value > 360:
            raise ValueError("Azimuth out of range. It should be between 0 and 360")
        return value

    # @field_validator("ROLL")
    # @classmethod
    # def validate_roll(cls, value: float) -> float:
    #     if value < -181 or value > 181:
    #         raise ValueError("")
    #     return value

    # @field_validator("PITCH")
    # @classmethod
    # def validate_pitch(cls, value: float) -> float:
    #     if value < -181 or value > 181:
    #         raise ValueError("")
    #     return value
    
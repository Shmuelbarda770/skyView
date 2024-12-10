from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List

class IncomingData(BaseModel):
    azimuth: float
    coordinate: List[float]
    height: float
    timeOfLastKnownLocation: str


    @field_validator("timeOfLastKnownLocation")
    @classmethod
    def validate_time_of_last_known_location(cls, value: str) -> str:
        if len(value) < 20 or len(value) > 30:
            pass
            # addlog
        return value

    @field_validator("coordinate")
    @classmethod
    def validate_coordinate(cls, value: List[float]) -> List[float]:
        if len(value) != 2:
            pass
            # addlog
        
        latitude, longitude = value

        if not (10 <= latitude <= 50):
            pass
            # addlog
        if not (10 <= longitude <= 50):
            pass
            # addlog
        
        return value

    @field_validator("height")
    @classmethod
    def validate_height(cls, value: float) -> float:
        if value < 0 or value > 5000:
           pass
            # addlog
        return value

    @field_validator("azimuth")
    @classmethod
    def validate_azimuth(cls, value: float) -> float:
        if value < 0 or value > 360:
            pass
            # addlog
        return value

    # @field_validator("roll")
    # @classmethod
    # def validate_roll(cls, value: float) -> float:
    #     if value < -181 or value > 181:
    #         pass
            # addlog
    #     return value

    # @field_validator("pitch")
    # @classmethod
    # def validate_pitch(cls, value: float) -> float:
    #     if value < -181 or value > 181:
    #        pass
            # addlog
    #     return value


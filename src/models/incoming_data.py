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
            raise ValueError("timeOfLastKnownLocation must be between 20 and 30 characters")
        return value

    @field_validator("coordinate")
    @classmethod
    def validate_coordinate(cls, value: List[float]) -> List[float]:
        if len(value) != 2:
            raise ValueError("Coordinate must have exactly two elements: [latitude, longitude]")
        
        latitude, longitude = value
        if not (10 <= latitude <= 50):
            raise ValueError("Latitude must be between 10 and 50")
        if not (10 <= longitude <= 50):
            raise ValueError("Longitude must be between 10 and 50")
        
        return value

    @field_validator("height")
    @classmethod
    def validate_height(cls, value: float) -> float:
        if value < 0 or value > 5000:
            raise ValueError("Height must be between 0 and 5000 meters")
        return value

    @field_validator("azimuth")
    @classmethod
    def validate_azimuth(cls, value: float) -> float:
        if value < 0 or value > 360:
            raise ValueError("Azimuth must be between 0 and 360 degrees")
        return value

    # @field_validator("roll")
    # @classmethod
    # def validate_roll(cls, value: float) -> float:
    #     if value < -181 or value > 181:
    #         raise ValueError("Roll must be between -181 and 181 degrees")
    #     return value

    # @field_validator("pitch")
    # @classmethod
    # def validate_pitch(cls, value: float) -> float:
    #     if value < -181 or value > 181:
    #         raise ValueError("Pitch must be between -181 and 181 degrees")
    #     return value


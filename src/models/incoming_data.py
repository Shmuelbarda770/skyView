from pydantic import BaseModel, Field, ValidationError, field_validator



class IncomingData(BaseModel):
    azimuth: float
    coordinate: dict  
    height: float
    timeOfLastKnownLocation: str

    @field_validator("timeOfLastKnownLocation")
    @classmethod
    def validate_time_of_last_known_location(cls, value: str) -> str:
        if len(value) < 20 or len(value) > 30:
            raise ValueError("")
        return value


    @field_validator("coordinate")
    @classmethod
    def validate_coordinate(cls, value):
        if len(value) != 2:
            raise ValueError("")
        
        latitude = value['latitude']
        longitude = value['longitude']

        if not (10 <= latitude <= 50):
            raise ValueError("")
        
        if not (10 <= longitude <= 50):
            raise ValueError("")
        
        return value


    @field_validator("height")
    @classmethod
    def validate_height(cls, value: float) -> float:
        if value < 0 or value > 5000:
            raise ValueError("")
        return value


    @field_validator("azimuth")
    @classmethod
    def validate_azimuth(cls, value: float) -> float:
        if value < 0 or value > 360:
            raise ValueError("")
        return value


    # def validate_roll(cls, value: float) -> float:
    #     if value < -181 or value > 181:
    #         raise ValueError("")
    #     return value


    # def validate_pitch(cls, value: float) -> float:
    #     if value < -181 or value > 181:
    #         raise ValueError("")
    #     return value





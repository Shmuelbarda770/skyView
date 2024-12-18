import re
from flet import TextField, ElevatedButton

class FieldValidator:

    @staticmethod
    def _validate_route_id(value: str) -> bool:
        pattern :str= r'^[a-zA-Z0-9_]{1,20}$'
        match: bool =bool(re.fullmatch(pattern, value))
        return match

    @staticmethod
    def _validate_platform_name(value: str) -> bool:
        pattern:str = r'^[A-Z]{3}$'
        match: bool = bool(re.fullmatch(pattern, value))
        return match

    @staticmethod
    def _validate_platform_id(value: str) -> bool:
        pattern :str= r'^[0-9]{1,3}$'
        match: bool = bool(re.fullmatch(pattern, value))
        return match

    @staticmethod
    def _validate_date(value: str) -> bool:
        pattern :str= r'^(((19)|(20))[0-9]{2})-((0[1-9])|(1[0-2]))-((0[1-9])|([1-2][0-9])|(3[01]))$'
        match: bool = bool(re.fullmatch(pattern, value))
        return match

    @staticmethod
    def _validate_platform_flight_index(value: str) -> bool:
        pattern:str = r'^[0-9]{1,4}$'
        match: bool = bool(re.fullmatch(pattern, value))
        return match


    @staticmethod
    def validate_all_field(route_id:TextField, Platform_flight_index:TextField, platform_id:TextField, platform_name:TextField, date:ElevatedButton)-> bool:
        route_id_value:str = route_id.value
        platform_flight_index_value :str= Platform_flight_index.value
        platform_id_value :str= platform_id.value
        platform_name_value :str= platform_name.value
        date_value:str = date.text

        if (not FieldValidator._validate_route_id(route_id_value) or
            not FieldValidator._validate_platform_name(platform_name_value) or
            not FieldValidator._validate_platform_id(platform_id_value) or
            not FieldValidator._validate_platform_flight_index(platform_flight_index_value) or
            not FieldValidator._validate_date(date_value)):
            
            return False  
        
        return True

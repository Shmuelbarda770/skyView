import re

class FieldValidator:

    @staticmethod
    def validate_route_id(value: str) -> bool:
        pattern = r'^[a-zA-Z0-9_]{1,20}$'
        match=re.fullmatch(pattern, value)
        return match

    @staticmethod
    def validate_platform_name(value: str) -> bool:
        pattern = r'^[A-Z]{3}$'
        match= bool(re.fullmatch(pattern, value))
        return match

    @staticmethod
    def validate_platform_id(value: str) -> bool:
        pattern = r'^[0-9]{1,3}$'
        match= bool(re.fullmatch(pattern, value))
        return match

    @staticmethod
    def validate_date(value: str) -> bool:
        pattern = r'^(((19)|(20))[0-9]{2})-((0[1-9])|(1[0-2]))-((0[1-9])|([1-2][0-9])|(3[01]))$'
        match= bool(re.fullmatch(pattern, value))
        return match

    @staticmethod
    def validate_platform_flight_index(value: str) -> bool:
        pattern = r'^[0-9]{1,4}$'
        match= bool(re.fullmatch(pattern, value))
        return match

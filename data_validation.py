import re

def validate_float(value) -> bool:
    pattern=r'^[0-9]{2}\.[0-9]{2,}$'
    x = re.match(pattern, value)
    return bool(x)


def validate_timeOfLastKnownLocation(value) -> bool:
    pass

def validate_coordinate(value) -> bool:
    pass

def validate_height(value) -> bool:
    pass

def validate_roll(value) -> bool:
    pass

def validate_pitch(value) -> bool:
    pass

def validate_azimuth(value) -> bool:
    pattern=r''


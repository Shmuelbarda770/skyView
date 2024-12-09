

def validate_timeOfLastKnownLocation(value) -> bool:
    if(len(value)<10 or len(value)>30):
        return False
   
    return True


def validate_coordinate(value: object) -> bool:
    if not isinstance(value, list) or len(value) != 2:
        return False
    
    latitude, longitude = value
    
    if latitude < 0 or latitude > 50:
        return False
    
    if longitude < 0 or longitude > 50:
        return False
    
    return True


def validate_height(value) -> bool:
    if not is_float(value):
        return False
    
    height_float = float(value)
    if height_float < 0 or height_float > 5000:
        return False
    
    return True


def validate_azimuth(value) -> bool:
    if not is_float(value):
        return False
    azimuth_float = float(value)
    if azimuth_float < 0 or azimuth_float > 360:
        return False
    
    return True


def validate_roll(value) -> bool:
    if not is_float(value):
        return False

    roll_float = float(value)
    if roll_float < -181 or roll_float > 181:
        return False
    
    return True


def validate_pitch(value) -> bool:
    if not is_float(value):
        return False

    pitch_float = float(value)
    if pitch_float < -181 or pitch_float > 181:
        return False
    
    return True


def is_float(value) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

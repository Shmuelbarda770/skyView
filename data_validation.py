import re
    

def validate_timeOfLastKnownLocation(value) -> bool:
    if(len(value)<20 or len(value)>30):
        return False
    pattern = r'^(((19)|(20))[0-9]{2})-((0[1-9]|1[0-2]))-((0[1-9])|([1-2][0-9])|(3[01]))[A-Z ]?(([0-1][0-9]|(2[0-3])):([0-5][0-9]):([0-5][0-9])[A-Z]?)$'
    match  = re.fullmatch (pattern, value)
    return bool(match)

def validate_coordinate(value) -> bool:
    if not isinstance(value,object) and len(value)!=2:
        return False
    
    if (value[0]>50 or value[0]<10) and (value[1]>50 or value[1]<10):
        return
    
    return True

def validate_height(value) -> bool:
    height_int=int(value)
    if(height_int<0 or height_int>5000):
        return False
    return True

def validate_roll(value) -> bool:
    roll_float=float(value)
    if roll_float>181 or roll_float<-181:
        return False
    return True

def validate_pitch(value) -> bool:
    pitch_float=float(value)
    if pitch_float>181 or pitch_float<-181:
        return False
    return True

def validate_azimuth(value) -> bool:
    azimuth_float=float(value)
    if azimuth_float>360 or azimuth_float<0:
        return False
    return True



import re


def validate_timeOfLastKnownLocation(value) -> bool:
    if(len(value)<10 or len(value)>30):
        return False
   
    return True

def validate_coordinate(value) -> bool:
    if not isinstance(value,object) and len(value)!=2:
        return False
    
    if (value[0]>50 or value[0]<0) and (value[1]>50 or value[1]<0):
        return False
    
    return True

def validate_height(value) -> bool:
    height_int=int(value)
    if(height_int<0 or height_int>5000):
        return False
    return True

# def validate_roll(value) -> bool:
#     roll_float=float(value)
#     if roll_float>181 or roll_float<-181:
#         return False
#     return True

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



# [{'azimuth': 309.92948031140907, 'height': 266.0776023199988, 'droneId': 2, 'coordinate': [32.97796967368646, 35.5731825255995], 'timeOfLastKnownLocation': '2024-12-01 08:11:05.566139'}]

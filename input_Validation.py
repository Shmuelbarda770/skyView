import re

def validate_string(value:str) ->bool:
    pattern = r'^[a-zA-Z\s]{2,20}$'
    match  = re.fullmatch (pattern, value)
    return bool(match)

def validate_int(value:str)-> bool :
    pattern = r'^[0-9]{2,20}$'
    match  = re.fullmatch (pattern, value)
    return bool(match)

def validate_float(value:str) -> bool:
    pattern = r'^[-]?\d+\.\d{2,20}$'
    match  = re.fullmatch(pattern, value)
    return bool(match)

def validate_date(value):
    pattern = r'^0?[0-9]{1,2}\-0?[0-9]{1,2}\-[0-9]{4}$'
    match  = re.fullmatch(pattern, value)
    return bool(match)

def validate_len_of_value(value):
    if len(value)>20 or len(value)<2:
        return False
    return True



import re

def validate_float(value) -> bool:
    pattern=r'^[0-9]{2}\.[0-9]{2,}$'
    x = re.match(pattern, value)
    return bool(x)
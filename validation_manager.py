from data_validation import validate_azimuth,validate_coordinate,validate_height,validate_timeOfLastKnownLocation
from input_Validation import validate_date,validate_Platform_flight_index,validate_platform_id,validate_platform_name,validate_route_id
from updatePage import show_error_in_screen


def validate_json(data_conversion,running_problems,logger):
    try:
        if validate_azimuth(data_conversion['azimuth']) and validate_coordinate(data_conversion['coordinate']) and validate_height(data_conversion['height']) and validate_timeOfLastKnownLocation(data_conversion['timeOfLastKnownLocation']):
            return True
        return False
    except Exception as e:
        show_error_in_screen(running_problems,"Problem with validate json")
        logger.warning(f'Problem with validate json, and the error is:{e},the data is: {data_conversion}')


def input_entered_and_valid_input(is_details_entered,route_id,Platform_flight_index,platform_id,platform_name,date,output,page):
        
        route_id_value = route_id.value
        Platform_flight_index_value = Platform_flight_index.value
        platform_id_value = platform_id.value
        platform_name_value = platform_name.value
        date_value = date.text

        
        if (not validate_route_id(route_id_value) or
            not validate_platform_name(platform_name_value) or
            not validate_platform_id(platform_id_value) or
            not validate_Platform_flight_index(Platform_flight_index_value) or
            not validate_date(date_value)):
            
            output.value = "All inputs required"
            page.update()
            return False  
        
        
        is_details_entered = True
        output.value = ""
        return True  
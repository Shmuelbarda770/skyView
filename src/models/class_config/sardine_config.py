from pydantic import BaseModel
from typing import Callable

class SardineConfig(BaseModel):
    route_id: str
    platform_flight_index: int
    platform_id: str
    platform_name: str
    date: str
    update_connection_status_message:  Callable[[str], None]
    show_error_in_screen:  Callable[[str], None]
    increment_received_json_counter:  Callable[[], None]
    increment_send_json_counter:  Callable[[], None]
    update_traffic_light_status:  Callable[[str], None]
    update_ui_when_send_data:  Callable[[], None]
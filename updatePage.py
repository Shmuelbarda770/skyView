

def light(status_indicator_green, status_indicator_red, status_indicator_yellow, color_status):
    status_indicator_red.visible = False
    status_indicator_yellow.visible = False
    status_indicator_green.visible = False

    if color_status == "red":
        status_indicator_red.visible = True
    elif color_status == "yellow":
        status_indicator_yellow.visible = True
    elif color_status == "green":
        status_indicator_green.visible = True

    status_indicator_red.update()
    status_indicator_yellow.update()
    status_indicator_green.update()


def message_view(status_connection,message):
    status_connection.value=message
    status_connection.update()


def add_num_cont_json_received(cont_received):
    new_value=int(cont_received.value)+1
    cont_received.value=str(new_value)
    cont_received.update()


def add_num_cont_send_json_to_cloud(cont_send):
    new_value=int(cont_send.value)+1
    cont_send.value=str(new_value)
    cont_send.update()


def show_error_in_screen(running_problems,problem):
    running_problems.value=""
    running_problems.value=problem
    running_problems.update()

 
def disabled_input(status_disabled,route_id,Platform_flight_index,platform_id,
                   platform_name,date,status_indicator_red,status_indicator_yellow,status_indicator_green):
    
    route_id.disabled = status_disabled
    Platform_flight_index.disabled = status_disabled
    platform_id.disabled = status_disabled
    platform_name.disabled =status_disabled
    date.disabled = status_disabled

    if status_disabled==False:
        status_indicator_red.visible=True
        status_indicator_yellow.visible=False
        status_indicator_green.visible=False
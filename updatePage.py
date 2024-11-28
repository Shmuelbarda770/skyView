import time

def blink_light(light, color_on, color_off, times=3, interval=0.5):
    for _ in range(times):
        light.bgcolor = color_on
        light.update()
        time.sleep(interval)
        light.bgcolor = color_off
        light.update()
        time.sleep(interval)
    light.bgcolor=color_on
    light.update()

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


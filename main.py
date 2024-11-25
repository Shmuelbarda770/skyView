import threading
import flet as ft
from flet import Page, TextField, ElevatedButton, Row, Column
from datetime import datetime
from drone_comm_system import open_socket, stop
from input_Validation import validate_date, validate_int, validate_string

def main(page: Page):
   
    page.title = "skyView"
    page.window.width = 600
    page.window.height = 600
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

   
    is_details_entered = False
    thread_01_status = threading.Event()

   
    route_id = TextField(label="Route id", width=200, height=60, fill_color='blue-light', max_length=20)
    flight_id = TextField(label="Flight id", width=200, height=60, fill_color='blue-light', max_length=20)
    platform_id = TextField(label="Platform id", width=200, height=60, fill_color='blue-light', max_length=3)
    platform_name = TextField(label="Platform name", width=200, height=60, fill_color='blue-light', max_length=20)
    date = ft.TextField(
        label="Date",
        value=datetime.now().strftime('%d-%m-%Y'),
        width=200,
        fill_color="blue-light"
    )

    
    submit_button = ElevatedButton(text="Submit", width=200)
    start_stop_button = ElevatedButton(text="start", width=200, bgcolor="green")

   
    def switch_to_start_stop(e):
        nonlocal is_details_entered

        route_id_value = route_id.value
        flight_id_value = flight_id.value
        platform_id_value = platform_id.value
        platform_name_value = platform_name.value
        date_value = date.value

     
        if (not validate_string(route_id_value) or
            not validate_string(flight_id_value) or
            not validate_int(platform_id_value) or
            not validate_string(platform_name_value) or
            not validate_date(date_value)):
            page.add(ft.Text("Please enter all fields.", color="red"))
            page.update()
            return

       
        is_details_entered = True
        update_view()

    
    def start_stop_handler(e):
        if thread_01_status.is_set():
            print("stop")
            thread_01_status.clear()
            stop(thread_01_status)
            start_stop_button.text = "start"
            start_stop_button.bgcolor = "green" 
        else:
            print("start")
            thread_01_status.set()
            start_stop_button.text = "stop"
            start_stop_button.bgcolor = "red"
            open_socket(thread_01_status, route_id.value, flight_id.value, platform_id.value, platform_name.value, date.value)
        start_stop_button.update()
        page.update()

    
    def update_view():
        page.controls.clear()
        if not is_details_entered:
            page.add(
                Row(
                    controls=[Column([route_id, flight_id, platform_id, platform_name, date, submit_button])],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )
        else:
            page.add(
                Row(
                    controls=[start_stop_button],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )
        page.update()

    
    submit_button.on_click = switch_to_start_stop
    start_stop_button.on_click = start_stop_handler

    
    update_view()

if __name__ == "__main__":
    ft.app(target=main)

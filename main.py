
import threading
import flet as ft
from flet import Page, TextField, ElevatedButton, Row, Column,Text,DatePicker
from datetime import datetime
from drone_comm_system import open_socket, stop
from input_Validation import validate_date,validate_Platform_flight_index,validate_platform_id,validate_platform_name,validate_route_id
from flet import colors as cl


def main(page: Page):


    thread_01_status = threading.Event()

    page.title = "Sky View"
    page.window.width = 900
    page.window.height = 700
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.bgcolor = "#f0f4f8"
    page.padding = 20
    is_details_entered = False
    is_processing = False 
    page.bgcolor = cl.BLUE_GREY_900

    title=Text("Drone Management Dashboard",size=30,weight="bold",color=cl.CYAN,text_align="center")
    route_id = TextField(label="Route id",bgcolor=cl.GREY_200, width=250, height=60, fill_color='blue-light', max_length=20,value='ffghghfsfh',hint_text="Only letters or numbers",color='black',text_align="center",border_radius=8)
    Platform_flight_index = TextField(label="Platform flight index",bgcolor=cl.GREY_200, width=250, height=60, fill_color='blue-light', max_length=3,value='ABC',hint_text="Only uppercase letters",color='black',text_align="center",border_radius=8)
    platform_id = TextField(label="Platform id", width=250,bgcolor=cl.GREY_200, height=60, fill_color='blue-light', max_length=3,value='232',hint_text="Only numbers",color='black',text_align="center",border_radius=8)
    platform_name = TextField(label="Platform name",bgcolor=cl.GREY_200, width=250, height=60, fill_color='blue-light' ,max_length=3,value='454',hint_text="Only numbers",color='black',text_align="center",border_radius=8)
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER


    date_for_json=None
    def handle_change(e):
        date_for_json=e.control.value.strftime('%Y-%m-%d')
        print(date_for_json)
        

    date_now=datetime.now()
    date = ft.ElevatedButton(
        "Pick Date",
        icon=ft.icons.CALENDAR_MONTH,
        on_click=lambda e: page.open(
            ft.DatePicker(
                first_date=datetime(year=date_now.year, month=date_now.month, day=date_now.day),
                last_date=datetime(year=date_now.year+15, month=date_now.month, day=date_now.day),
                on_change=handle_change
            )
        ),
        bgcolor='#00ACC1',
        width=250,
        height=50
    )

    output=ft.Text(value="",color='red')
    
    status_indicator_red = ft.Container(
        width=20,
        height=20,
        bgcolor="red",
        border_radius=25,
        alignment=ft.alignment.center
    )
    status_indicator_yellow = ft.Container(
        width=20,
        height=20,
        bgcolor="yellow",
        border_radius=25,
        alignment=ft.alignment.center
    )
    status_indicator_green = ft.Container(
        width=20,
        height=20,
        bgcolor="green",
        border_radius=25,
        alignment=ft.alignment.center
    )
    status_connection= ft.Text(value="",color="white")
    cont_json_received= ft.Text(value="0",color="white")
    explanation_text_cont_json_received = ft.Text(value="Count of received JSON data from the drone: ",color="white")
    cont_send_json_to_cloud= ft.Text(value="0",color="white")
    explanation_text_cont_send_json_to_cloud = ft.Text(value="Number of JSON sent to the cloud: ",color="white")
    running_problems= ft.Text(value="",color="red")
    explanation_running_problems = ft.Text(value="Error: ",color="red")
   
    

    submit_button = ElevatedButton(text="Submit", width=200)
    start_stop_button = ElevatedButton(text="start", width=200, bgcolor=ft.colors.GREEN)

    def start_stop_handler(e):
        nonlocal is_processing
        if is_processing:
            return
        
        is_processing = True
        try:
            if thread_01_status.is_set():
                print("stop")
                route_id.disabled = False
                Platform_flight_index.disabled = False
                platform_id.disabled = False
                platform_name.disabled = False
                date.disabled = False
                start_stop_button.text = "start"
                start_stop_button.bgcolor = 'green'
                start_stop_button.update()
                page.update()
                thread_01_status.clear()
                stop(thread_01_status,status_indicator_red,status_connection)
            else:
                print("start")
                route_id.disabled = True
                Platform_flight_index.disabled = True
                platform_id.disabled = True
                platform_name.disabled = True
                date.disabled = True
                start_stop_button.text = "stop"
                start_stop_button.bgcolor = 'red'
                start_stop_button.update()
                page.update()
                thread_01_status.set()
                open_socket(thread_01_status, route_id.value, Platform_flight_index.value, 
                          platform_id.value, platform_name.value, date_for_json,status_indicator_red,
                          status_indicator_yellow,status_indicator_green,status_connection,cont_json_received,cont_send_json_to_cloud)
        finally:
            is_processing = False



    def switch_to_start_stop(e):
        nonlocal is_details_entered
 
        route_id_value = route_id.value
        Platform_flight_index_value = Platform_flight_index.value
        platform_id_value = platform_id.value
        platform_name_value = platform_name.value
        date_value = date_for_json



        if (not validate_route_id(route_id_value) or
            not validate_platform_name(Platform_flight_index_value) or
            not validate_platform_id(platform_id_value) or
            not validate_Platform_flight_index(platform_name_value) or
            not validate_date(date_value)):
            
            output.value = "All inputs required"
            page.update()
            return

        
        is_details_entered = True
        update_view()
    
    def update_view():
        page.controls.clear()

        page.add(
            Row(controls=[title],alignment=ft.MainAxisAlignment.CENTER),
            Row(
                controls=[platform_name, platform_id,date],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            Row(
                controls=[Platform_flight_index,route_id],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            ),
            Column(
                controls=[start_stop_button,status_connection],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            ),
            Row(
                controls=[status_indicator_red,status_indicator_yellow,status_indicator_green],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            ),
            Row(
                controls=[explanation_text_cont_json_received,cont_json_received,output],
                alignment=ft.MainAxisAlignment.START,
                spacing=20
                ),
            Row(
                controls=[explanation_text_cont_send_json_to_cloud,cont_send_json_to_cloud],
                alignment=ft.MainAxisAlignment.START,
                spacing=20
                ),
            Row(
                controls=[explanation_running_problems,running_problems],
                alignment=ft.MainAxisAlignment.START,
                spacing=20
            )

        )
        page.update()
    
    submit_button.on_click = switch_to_start_stop
    start_stop_button.on_click = start_stop_handler
    
    

    update_view()

if __name__ == "__main__":
    ft.app(target=main)

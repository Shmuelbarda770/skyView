
import flet as ft
from flet import Page, TextField, ElevatedButton, Row, Column, Text
from datetime import datetime
from flet import colors as cl, icons
from src.app_gui.style_util import base_fields_style, status_indicator_style
from src.app_gui.global_variables import global_variables_state
from src.app_gui.field_validator import FieldValidator
from src.sardine_lisener.socket_connection_handler import SocketThreadManager
import sys
import time
import os
import signal

class GUI:
    def __init__(self, page: Page):
        self.page = page
        self.date_now=datetime.now()
        self.connection_status_flag=global_variables_state["connection_status_flag"]
        self.initialize_page()
        self.create_elements()
        self.build_view()
        self.SocketThreadManager=SocketThreadManager(self.route_id, self.platform_flight_index, 
                                                     self.platform_id, self.platform_name, self.date,
                 self.status_indicator_unconnected,self.status_indicator_connected_and_receives_data,
                 self.status_indicator_send_to_cloud ,self.status_connection,
                 self.received_json_counter,self.sent_json_counter,self.show_running_error,
                 self.increment_received_json_counter,self.increment_send_json_counter,self.update_traffic_light_status,self.page)
       

    def initialize_page(self):
        self.page.title = "Sky View"
        self.page.window.width = 900
        self.page.window.height = 700
        self.page.vertical_alignment = "center"
        self.page.horizontal_alignment = "center"
        self.page.bgcolor = cl.BLUE_GREY_900
        self.page.padding = 20

    def create_elements(self):
        self.title = Text(
            "Drone Management Dashboard",
            size=30,
            weight="bold",
            color=cl.CYAN,
            text_align="center",
        )

        self.route_id = TextField(
            **base_fields_style,
            label="Route id",
            max_length=20,
            hint_text="Letters or numbers",
            value='flight_12'
        )

        self.platform_flight_index = TextField(
            **base_fields_style,
            label="Platform flight index",
            max_length=4,
            value='1234',
            hint_text="Numbers only"
        )

        self.platform_id = TextField(
            **base_fields_style,
            label="Platform id",
            max_length=3,
            value="123",
            hint_text="Numbers only"
        )

        self.platform_name = TextField(
             **base_fields_style,
            label="Platform name",
            max_length=3,
            value="ABC",
            hint_text="Letters only"
        )

        self.start_button = ElevatedButton(text="Start", width=200, bgcolor=cl.GREEN)
        self.start_button.on_click = self.handle_start_click

        self.stop_button = ElevatedButton(text="Stop", width=200, bgcolor=cl.RED,visible=False)
        self.stop_button.on_click = self.handle_stop_click

        self.status_indicator_unconnected = ft.Container(**status_indicator_style, bgcolor="red", visible=True)
        self.status_indicator_connected_and_receives_data = ft.Container(**status_indicator_style, bgcolor="yellow", visible=False)
        self.status_indicator_send_to_cloud = ft.Container(**status_indicator_style, bgcolor="green",visible=False)

        self.status_connection = Text(value="", color="white")

        self.date = ft.ElevatedButton(
        "Pick Date",
        icon=icons.CALENDAR_MONTH,
        on_click=lambda e: self.page.open(
            ft.DatePicker(
                first_date=datetime(year=self.date_now.year, month=self.date_now.month, day=self.date_now.day),
                last_date=datetime(year=self.date_now.year+15, month=self.date_now.month, day=self.date_now.day),
                on_change=self._handle_change_date_view
            )
        ),
        bgcolor='#00ACC1',
        width=250,
        height=50
        )


        self.received_json_counter = ft.Text(value="0",color="white")
        self.explanation_text_received_json_counter = ft.Text(value="Count of received JSON data from the drone: ",color="white")
        self.sent_json_counter = ft.Text(value="0",color="white")
        self.explanation_text_sent_json_counter  = ft.Text(value="Number of JSON sent to the cloud: ",color="white")
        self.show_running_error= ft.Text(value="",color="red")
        self.explanation_show_running_error = ft.Text(value="Error: ",color="red")

        self.page.window.prevent_close=True
        self.page.window.on_event=self.handle_window_event




    def _handle_change_date_view(self,e):
        self.date.text= e.control.value.strftime("%Y-%m-%d")
        self.date.update()
        
    
    def handle_start_click(self,e):
        

        if not FieldValidator.validate_all_field(
                                            self.route_id,
                                            self.platform_flight_index,
                                            self.platform_id,
                                            self.platform_name,
                                            self.date
                                            ):
            self.show_error_in_screen("Some fields are missing. Please fill in all fields")
            return
        
        self.connection_status_flag.set()
        self.SocketThreadManager.open_socket_running()
        self.start_button.visible=False
        self.stop_button.visible=True
        self.show_error_in_screen("")
        self.set_input_fields_disabled_status()
        self.page.update()
        self.SocketThreadManager.open_socket_running()
        



    def handle_stop_click(self,e):
        self.SocketThreadManager.stop_socket_running()
        self.start_button.visible=True
        self.stop_button.visible=False
        self.page.update()
        


    def set_input_fields_disabled_status(self):

        self.route_id.disabled = True
        self.platform_flight_index.disabled = True
        self.platform_id.disabled = True
        self.platform_name.disabled = True
        self.date.disabled = True

        
        self.status_indicator_unconnected.visible = True
        self.status_indicator_connected_and_receives_data.visible = False
        self.status_indicator_send_to_cloud.visible = False


    def enable_input_fields(self):

        self.route_id.disabled = False
        self.platform_flight_index.disabled = False
        self.platform_id.disabled = False
        self.platform_name.disabled = False
        self.date.disabled = False

        
        self.status_indicator_unconnected.visible = True
        self.status_indicator_connected_and_receives_data.visible = False
        self.status_indicator_send_to_cloud.visible = False


    def show_error_in_screen(self,problem):
        self.show_running_error.value=""
        self.show_running_error.value=problem
        self.show_running_error.update()

    def increment_received_json_counter(self):
        new_value = int(self.received_json_counter.value) + 1
        self.received_json_counter.value = str(new_value)
        self.received_json_counter.update()


    def increment_send_json_counter(self):
        new_value = int(self.sent_json_counter.value) + 1
        self.sent_json_counter.value = str(new_value)
        self.sent_json_counter.update()


    def update_traffic_light_status(self,status_indicator):
        self.status_indicator_unconnected = False
        self.status_indicator_connected_and_receives_data = False
        self.status_indicator_send_to_cloud = False


        if status_indicator == "red":
            self.status_indicator_unconnected.visible = True
        elif status_indicator == "yellow":
            self.status_indicator_connected_and_receives_data.visible = True
        elif status_indicator == "green":
            self.status_indicator_send_to_cloud.visible = True

        
        self.status_indicator_unconnected.update()
        self.status_indicator_connected_and_receives_data.update()
        self.status_indicator_send_to_cloud.update()

    
    def update_connection_status_message(self, status_message):
        self.status_connection.value = status_message
        self.status_connection.update()



    def build_view(self):
        self.page.controls.clear()
        
        self.page.add(
            Row([self.title], alignment=ft.MainAxisAlignment.CENTER),
            Row(controls=[self.platform_name, self.platform_id,self.date],alignment=ft.MainAxisAlignment.CENTER,),
            Row([self.platform_flight_index, self.route_id],alignment=ft.MainAxisAlignment.CENTER,spacing=20,),
            Column([self.status_connection,self.start_button,self.stop_button],alignment=ft.MainAxisAlignment.CENTER,spacing=20,),
            Row([
                    self.status_indicator_unconnected,
                    self.status_indicator_connected_and_receives_data,
                    self.status_indicator_send_to_cloud,
                ],
                alignment=ft.MainAxisAlignment.CENTER,spacing=20),
            Row([self.explanation_text_received_json_counter, self.received_json_counter],alignment=ft.MainAxisAlignment.CENTER,spacing=20,),
            Row([self.explanation_text_sent_json_counter, self.sent_json_counter],alignment=ft.MainAxisAlignment.CENTER,spacing=20,),
            Row([self.explanation_show_running_error, self.show_running_error],alignment=ft.MainAxisAlignment.CENTER,spacing=20,)
        )

        self.page.update()

    def handle_window_event(self,e: ft.ControlEvent):
        if e.data == "close":
            self.page.window.prevent_close=False
            self.page.window.close()
            try:
                time.sleep(2)
                sys.exit(0)
            except SystemExit as e:
                os.kill(os.getpid(),signal.SIGTERM)


   






# if __name__ == "__main__":
#     def main(page: Page):
#        GUI(page)


#     ft.app(target=main)

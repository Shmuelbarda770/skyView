import sys
import time
import os
import signal
from datetime import datetime
from typing import Optional
import flet as ft
from flet import colors as cl, icons
from flet import Page, TextField, ElevatedButton, Row, Column, Text, Container, ProgressRing, ControlEvent

from src.GUI.style_util import base_fields_style, status_indicator_style
from src.models.class_config.config_data import ConfigData
from src.GUI.utils.field_validator import FieldValidator
from src.managers.sardine_manager import SardineManager


class GUI:
    def __init__(self, page: Page):
        self.page: Page = page
        self.date_now: datetime = datetime.now()
        self.finish_to_stop_all_tread: bool = False
        self.initialize_page()
        self.create_elements()
        self.build_view()

        self.config_data: ConfigData|None = None
        self.SardineManager:  Optional[SardineManager]  = None

    def initialize_page(self) -> None:
        self.page.title = "Sky View"
        self.page.window.width = 900
        self.page.window.height = 700
        self.page.vertical_alignment = "center"
        self.page.horizontal_alignment = "center"
        self.page.bgcolor = cl.BLUE_GREY_900
        self.page.padding = 20

    def config_data_for_class(self) -> dict:
        return {
            "route_id": self.route_id.value,
            "platform_flight_index": self.platform_flight_index.value,
            "platform_id": self.platform_id.value,
            "platform_name": self.platform_name.value,
            "date": self.date.text,
            "update_connection_status_message": self.update_connection_status_message,
            "show_error_in_screen": self.show_error_in_screen,
            "increment_received_json_counter": self.increment_received_json_counter,
            "increment_send_json_counter": self.increment_send_json_counter,
            "update_traffic_light_status": self.update_traffic_light_status,
            "update_ui_when_send_data": self.update_ui_when_send_data,
        }

    def create_elements(self):
        self.title: Text = Text(
            "Drone Management Dashboard",
            style=ft.TextThemeStyle.HEADLINE_SMALL,
            size=30,
            weight="bold",
            color=cl.CYAN,
            text_align="center",
        )

        self.route_id: TextField = TextField(
            **base_fields_style,
            label="Route id",
            max_length=20,
            hint_text="Letters or numbers",
            value="flight_12",
        )

        self.platform_flight_index: TextField = TextField(
            **base_fields_style, label="Platform flight index", max_length=4, value="1234", hint_text="Numbers only"
        )

        self.platform_id: TextField = TextField(
            **base_fields_style, label="Platform id", max_length=3, value="123", hint_text="Numbers only"
        )

        self.platform_name: TextField = TextField(
            **base_fields_style, label="Platform name", max_length=3, value="ABC", hint_text="Letters only"
        )

        self.start_button: ElevatedButton = ElevatedButton(
            text="Start", width=200, bgcolor=cl.GREEN, tooltip="Click to start", elevation=5
        )
        self.start_button.on_click = self.handle_start_click

        self.stop_button: ElevatedButton = ElevatedButton(
            text="Stop",
            width=200,
            bgcolor=cl.RED,
            visible=False,
            tooltip="Click to stop",
            elevation=5,
        )
        self.stop_button.on_click = self.handle_stop_click

        self.loading_when_program_not_finish: ProgressRing = ProgressRing(
            visible=False,
        )

        self.status_indicator_unconnected: Container = Container(**status_indicator_style, bgcolor="red", visible=True)
        self.status_indicator_connected_and_receives_data: Container = Container(
            **status_indicator_style, bgcolor="yellow", visible=False
        )
        self.status_indicator_send_to_cloud: Container = Container(
            **status_indicator_style, bgcolor="green", visible=False
        )

        self.status_connection: Text = Text(value="", color="white")

        self.date: ElevatedButton = ElevatedButton(
            "Pick Date",
            icon=icons.CALENDAR_MONTH,
            on_click=lambda e: self.page.open(
                ft.DatePicker(
                    first_date=datetime(year=self.date_now.year, month=self.date_now.month, day=self.date_now.day),
                    last_date=datetime(year=self.date_now.year + 15, month=self.date_now.month, day=self.date_now.day),
                    on_change=self._handle_change_date_view,
                )
            ),
            bgcolor="#00ACC1",
            width=250,
            height=50,
            tooltip="Select a date",
            elevation=5,
        )

        self.received_json_counter: Text = ft.Text(value="0", color="white")
        self.explanation_text_received_json_counter: Text = ft.Text(
            value="Count of received JSON data from the drone: ", color="white"
        )
        self.sent_json_counter: Text = ft.Text(value="0", color="white")
        self.explanation_text_sent_json_counter: Text = ft.Text(
            value="Number of JSON sent to the cloud: ", color="white"
        )
        self.show_running_error: Text = ft.Text(value="", color="red")
        self.explanation_show_running_error: Text = ft.Text(value="Error: ", color="red")

        self.page.window.prevent_close = True
        self.page.window.on_event = self.handle_window_event

    def _handle_change_date_view(self, e: ControlEvent):
        value: datetime = e.control.value
        self.date.text = value.strftime("%Y-%m-%d")

        self.date.update()

    def field_validator(self) -> bool:
        if FieldValidator.validate_all_field(
            self.route_id, self.platform_flight_index, self.platform_id, self.platform_name, self.date
        ):
            return True
        self.show_error_in_screen("")
        return False

    def handle_start_click(self, e: ControlEvent):

        if not self.field_validator():
            self.show_error_in_screen("Some fields are missing. Please fill in all fields")
            return

        self.config_data = ConfigData(**self.config_data_for_class())
        self.SardineManager = SardineManager(self.config_data)

        self.set_input_fields_disabled_status()

        self.SardineManager.start_listening_for_sardine()
        self.when_tread_finish_to_run_sardine_manager()
        self.update_traffic_light_status("red")

    def handle_stop_click(self, e: ControlEvent):
        if self.SardineManager is not None:
            self.SardineManager.stop_listening_for_sardine()
            self.when_tread_finish_to_run_add_loading()
            self.enable_input_fields()
            self.update_traffic_light_status("red")

    def when_tread_finish_to_run_add_loading(self) -> None:
        self.loading_when_program_not_finish.visible = True
        self.status_connection.value = ""
        self.show_error_in_screen("")
        self.set_all_element_in_page_disabled()

    def when_tread_finish_to_run_sardine_manager(self) -> None:
        self.loading_when_program_not_finish.visible = False
        self.set_all_element_in_page_enable()

    def set_all_element_in_page_disabled(self) -> None:
        all_element_in_page = {
            self.platform_name: TextField,
            self.platform_id: TextField,
            self.date: ElevatedButton,
            self.platform_flight_index: TextField,
            self.route_id: TextField,
            self.start_button: TextField,
        }
        for element in all_element_in_page:
            element.disabled = True
        self.page.update()

    def set_all_element_in_page_enable(self) -> None:
        all_element_in_page = {
            self.platform_name: TextField,
            self.platform_id: TextField,
            self.date: ElevatedButton,
            self.platform_flight_index: TextField,
            self.route_id: TextField,
            self.start_button: TextField,
        }
        for element in all_element_in_page:
            element.disabled = False
        self.page.update()

    def set_input_fields_disabled_status(self) -> None:

        self.start_button.visible = False
        self.stop_button.visible = True

        self.route_id.disabled = True
        self.platform_flight_index.disabled = True
        self.platform_id.disabled = True
        self.platform_name.disabled = True
        self.date.disabled = True

        self.status_indicator_unconnected.visible = True
        self.status_indicator_connected_and_receives_data.visible = False
        self.status_indicator_send_to_cloud.visible = False

        self.page.update()

    def enable_input_fields(self) -> None:

        self.start_button.visible = True
        self.stop_button.visible = False

        self.route_id.disabled = False
        self.platform_flight_index.disabled = False
        self.platform_id.disabled = False
        self.platform_name.disabled = False
        self.date.disabled = False

        self.status_indicator_unconnected.visible = True
        self.status_indicator_connected_and_receives_data.visible = False
        self.status_indicator_send_to_cloud.visible = False

        self.page.update()

    def update_ui_when_send_data(self) -> None:
        self.update_connection_status_message("Sending data to cloud")

        status_indicator_color = "green"
        self.update_traffic_light_status(status_indicator_color)

        self.increment_send_json_counter()

    def show_error_in_screen(self, problem: str) -> None:
        self.show_running_error.value = ""
        self.show_running_error.value = problem
        self.show_running_error.update()

    def increment_received_json_counter(self) -> None:
        new_value: int = int(self.received_json_counter.value) + 1
        self.received_json_counter.value = str(new_value)
        self.received_json_counter.update()

    def increment_send_json_counter(self) -> None:
        new_value: int = int(self.sent_json_counter.value) + 1
        self.sent_json_counter.value = str(new_value)
        self.sent_json_counter.update()

    def update_traffic_light_status(self, status_indicator_color: str) -> None:
        self.status_indicator_unconnected.visible = False
        self.status_indicator_connected_and_receives_data.visible = False
        self.status_indicator_send_to_cloud.visible = False

        if status_indicator_color == "red":
            self.status_indicator_unconnected.visible = True
        elif status_indicator_color == "yellow":
            self.status_indicator_connected_and_receives_data.visible = True
        elif status_indicator_color == "green":
            self.status_indicator_send_to_cloud.visible = True

        self.status_indicator_unconnected.update()
        self.status_indicator_connected_and_receives_data.update()
        self.status_indicator_send_to_cloud.update()

    def update_connection_status_message(self, status_message: str) -> None:
        self.status_connection.value = status_message
        self.status_connection.update()

    def handle_window_event(self, e: ControlEvent) -> None:
        if e.data == "close":
            self.page.window.prevent_close = False
            self.page.window.close()
            try:
                time.sleep(2)
                sys.exit(0)
            except SystemExit as e:
                os.kill(os.getpid(), signal.SIGTERM)

    def build_view(self) -> None:
        self.page.controls.clear()

        self.page.add(
            Row([self.title], alignment=ft.MainAxisAlignment.CENTER),
            Row(
                controls=[self.platform_name, self.platform_id, self.date],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            Row(
                [self.platform_flight_index, self.route_id],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            Column(
                [self.status_connection, self.start_button, self.stop_button],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            Row(
                [
                    self.status_indicator_unconnected,
                    self.status_indicator_connected_and_receives_data,
                    self.status_indicator_send_to_cloud,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            Row([self.loading_when_program_not_finish], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            Row(
                [self.explanation_text_received_json_counter, self.received_json_counter],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            Row(
                [self.explanation_text_sent_json_counter, self.sent_json_counter],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            Row(
                [self.explanation_show_running_error, self.show_running_error],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
        )

        self.page.update()

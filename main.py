import threading
import flet as ft
from flet import Page, TextField, ElevatedButton, Text, Row, Column
from flet_core import ControlEvent
import queue
import logging
from drone_comm_system import stop ,open_socket


logging.basicConfig(level=logging.INFO, filename='test.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def main(page: Page):
    page.title = "skyView"
    page.window.width = 500
    page.window.height = 500
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

   
    thread_01_status = threading.Event()

    route_id: TextField = TextField(label="route id", width=200, height=50, fill_color='blue-light')
    
    flight_id: TextField = TextField(label="flight id", width=200, height=50, fill_color='blue-light')

    platform_id: TextField = TextField(label="platform id", width=200, height=50, fill_color='blue-light')

    platform_name: TextField = TextField(label="platform name", width=200, height=50, fill_color='blue-light')

    date: TextField = TextField(label="date", width=200 , height=50, fill_color='blue-light')




    button: ElevatedButton = ElevatedButton(text="start", width=200)

    def click_handler(e: ControlEvent) -> None:
        if thread_01_status.is_set():
            stop(thread_01_status)
            # page.clean()
            button.text = 'Connecting to the drone'
        else:
            thread_01_status.set()
            open_socket(thread_01_status,route_id.value , flight_id.value , platform_id.value , platform_name.value , date.value)
            button.text = 'Stop connecting to the drone'
        page.update()

    button.on_click = click_handler

    page.add(
        Row(
            controls=[Column([route_id , flight_id , platform_id , platform_name , date , button])],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

if __name__ == "__main__":
    ft.app(target=main)

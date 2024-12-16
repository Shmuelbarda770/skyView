
# import flet as ft
# from flet import Page, TextField, ElevatedButton, Row, Column,Text
# from datetime import datetime
# from drone_comm_system import open_socket, stop,event
# from flet import colors as cl,icons
# from validation_manager import input_entered_and_valid_input
# from updatePage import disabled_input
# import sys
# import os
# import signal
# import time

# def main(page: Page):
#     page.title = "Sky View"
#     page.window.width = 900
#     page.window.height = 700
#     page.vertical_alignment = "center"
#     page.horizontal_alignment = "center"
#     page.bgcolor = "#f0f4f8"
#     page.padding = 20
#     is_details_entered = False
#     page.bgcolor = cl.BLUE_GREY_900

#     title=Text("Drone Management Dashboard",size=30,weight="bold",color=cl.CYAN,text_align="center")
#     route_id = TextField(label="Route id",bgcolor=cl.GREY_200, width=250, height=60, fill_color='blue-light', max_length=20,value='flight_12',hint_text="Letters or numbers",color='black',text_align="center",border_radius=8)
#     Platform_flight_index = TextField(label="Platform flight index",bgcolor=cl.GREY_200, width=250, height=60, fill_color='blue-light', max_length=4,value='1234',hint_text="Numbers only",color='black',text_align="center",border_radius=8)
#     platform_id = TextField(label="Platform id", width=250,bgcolor=cl.GREY_200, height=60, fill_color='blue-light', max_length=3,value="123",hint_text="Numbers only",color='black',text_align="center",border_radius=8)
#     platform_name = TextField(label="Platform name",bgcolor=cl.GREY_200, width=250, height=60, fill_color='blue-light' ,max_length=3,value="ABC",hint_text="Letters only",color='black',text_align="center",border_radius=8)
#     page.horizontal_alignment = ft.CrossAxisAlignment.CENTER


    
    
    
#     def handle_change(e):
#         date.text= e.control.value.strftime("%Y-%m-%d")
#         date.update()
        
#     date_now=datetime.now()
#     date = ft.ElevatedButton(
#         "Pick Date",
#         icon=icons.CALENDAR_MONTH,
#         on_click=lambda e: page.open(
#             ft.DatePicker(
#                 first_date=datetime(year=date_now.year, month=date_now.month, day=date_now.day),
#                 last_date=datetime(year=date_now.year+15, month=date_now.month, day=date_now.day),
#                 on_change=handle_change
#             )
#         ),
#         bgcolor='#00ACC1',
#         width=250,
#         height=50
#     )
    
#     output=ft.Text(value="",color='red')
#     ## TODO: add new button to stop
#     status_indicator_red = ft.Container(width=20,height=20,bgcolor="red",border_radius=25,alignment=ft.alignment.center,visible=True)
#     status_indicator_yellow = ft.Container(width=20,height=20,bgcolor="yellow",border_radius=25,alignment=ft.alignment.center, visible=False)
#     status_indicator_green = ft.Container(width=20,height=20,bgcolor="green",border_radius=25,alignment=ft.alignment.center, visible=False)
    
#     status_connection= ft.Text(value="",color="white")
#     cont_json_received= ft.Text(value="0",color="white")
#     explanation_text_cont_json_received = ft.Text(value="Count of received JSON data from the drone: ",color="white")
#     cont_send_json_to_cloud= ft.Text(value="0",color="white")
#     explanation_text_cont_send_json_to_cloud = ft.Text(value="Number of JSON sent to the cloud: ",color="white")
#     running_problems= ft.Text(value="",color="red")
#     explanation_running_problems = ft.Text(value="Error: ",color="red")
    

#     start_stop_button = ElevatedButton(text="start", width=200, bgcolor=cl.GREEN)

#     event_finish_to_collect_data = False ## TODO: look at ritzratz how to work with global variables

#     def start_stop_handler(e): ##TODO: take out this function. functions should be around 50 lines
#         nonlocal event_finish_to_collect_data

#         if not input_entered_and_valid_input(is_details_entered,route_id,Platform_flight_index,platform_id,platform_name,date,output,page): ## TODO: this function check if the input is valid
#             return

#         try: ## TODO: can be separated into two different functions 
#             if event.is_set(): ## TODO: event name is unclear
#                 ## TODO: put this code inside a function
#                 output.value = "" ## TODO: output what ?
#                 output.update() ## TODO: not needed
#                 event_finish_to_collect_data=True
#                 disabled_input_on_start = False ## TODO: name is not clear should be in the global files
#                 disabled_input(disabled_input_on_start, route_id, Platform_flight_index, platform_id, platform_name,
#                             date, status_indicator_red, status_indicator_yellow, status_indicator_green) ## TODO: name should be more clear
#                 start_stop_button.text = "Start"
#                 start_stop_button.bgcolor = cl.GREEN
#                 start_stop_button.update()  ## TODO: not needed
#                 page.update()
#                 stop() ## TODO: not indicative 
#             else:
#                 if event_finish_to_collect_data:
#                     output.value = "The system is already running"
#                     output.color = "red"
#                     output.update()
#                     return
                
#                 disabled_input_on_stop = True
#                 disabled_input(disabled_input_on_stop, route_id, Platform_flight_index, platform_id, platform_name, date,
#                             status_indicator_red, status_indicator_yellow, status_indicator_green)
#                 start_stop_button.text = "Stop"
#                 start_stop_button.bgcolor = cl.RED
#                 start_stop_button.update()
#                 page.update()
#                 event.set() 
#                 open_socket(event, route_id.value, Platform_flight_index.value,
#                             platform_id.value, platform_name.value, date.text, status_indicator_red,
#                             status_indicator_yellow, status_indicator_green, status_connection,
#                             cont_json_received, cont_send_json_to_cloud, running_problems) ## TODO: function name is not clear
#                 event_finish_to_collect_data=False
#         except Exception as e:
#             pass
 


#     def update_view(): ## TODO: this function should be called build view.
#         page.controls.clear()

#         page.add(
#             Row(controls=[title],alignment=ft.MainAxisAlignment.CENTER),
#             Row(controls=[platform_name, platform_id,date],alignment=ft.MainAxisAlignment.CENTER),
#             Row(controls=[Platform_flight_index,route_id],alignment=ft.MainAxisAlignment.CENTER,spacing=20),
#             Column(controls=[start_stop_button,status_connection],alignment=ft.MainAxisAlignment.CENTER,spacing=20),
#             Row(controls=[status_indicator_red,status_indicator_yellow,status_indicator_green],alignment=ft.MainAxisAlignment.CENTER,spacing=20),
#             Row(controls=[explanation_text_cont_json_received,cont_json_received,output],alignment=ft.MainAxisAlignment.START,spacing=20),
#             Row(controls=[explanation_text_cont_send_json_to_cloud,cont_send_json_to_cloud],alignment=ft.MainAxisAlignment.START,spacing=20),
#             Row(controls=[explanation_running_problems,running_problems],alignment=ft.MainAxisAlignment.START,spacing=20)
#         )

        
#         page.update()

    
#     start_stop_button.on_click = start_stop_handler

#     update_view()

    
#     def handle_window_event(e: ft.ControlEvent):
#         if e.data == "close":
#             page.window.prevent_close=False
#             page.window.close()
#             try:
#                 time.sleep(2)
#                 sys.exit(0)
#             except SystemExit as e:
#                 os.kill(os.getpid(),signal.SIGTERM)


#     page.window.prevent_close=True
#     page.window.on_event=handle_window_event

# if __name__ == "__main__":
#     ft.app(target=main) ## TODO: septate the gui from this file need to be under folder gui
#     ## the structure should contain src folder, inside gui , business logic, utils ....
#     ## requirements, spec, readme ... (look at ritzratz)

import flet as ft
from flet import Page
from src.GUI.gui import GUI

if __name__ == "__main__":
   def main(page: Page):
       GUI(page)

   ft.app(target=main)
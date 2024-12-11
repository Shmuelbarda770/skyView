
import flet as ft
from flet import Page, TextField, ElevatedButton, Row, Column, Text
from datetime import datetime
from flet import colors as cl, icons
from src.app_gui.style_util import base_fields_style, status_indicator_style
from src.app_gui.global_variables import global_variables_state
from src.app_gui.field_validator import FieldValidator
# from sardine_lisener.s

class GUI:
    def __init__(self, page: Page):
        self.page = page
        self.date_now=datetime.now()
        self.connection_status_flag=global_variables_state["connection_status_flag"]
        self.initialize_page()
        self.create_elements()
        self.build_view()
       

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

        self.status_indicator_unconnected = ft.Container(
            **status_indicator_style, bgcolor="red", visible=True
        )
        self.status_indicator_connected_and_receives_data = ft.Container(
            **status_indicator_style, bgcolor="yellow", visible=False
        )
        self.status_indicator_send_to_cloud = ft.Container(
            **status_indicator_style, bgcolor="green",visible=False
        )

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


        self.cont_json_received= ft.Text(value="0",color="white")
        self.explanation_text_cont_json_received = ft.Text(value="Count of received JSON data from the drone: ",color="white")
        self.cont_send_json_to_cloud= ft.Text(value="0",color="white")
        self.explanation_text_cont_send_json_to_cloud = ft.Text(value="Number of JSON sent to the cloud: ",color="white")
        self.show_running_error= ft.Text(value="",color="red")
        self.explanation_show_running_error = ft.Text(value="Error: ",color="red")






    def _handle_change_date_view(self,e):
        self.date.text= e.control.value.strftime("%Y-%m-%d")
        self.date.update()
        
    
    def handle_start_click(self,e):
        self.start_button.visible=True
        self.stop_button.visible=False

        if not FieldValidator.validate_all_field(
                                            self.route_id,
                                            self.platform_flight_index,
                                            self.platform_id,
                                            self.platform_name,
                                            self.date,
                                            self.page):
            return

            
        self.set_input_disabled_status()
        



    def handle_stop_click(self):
        self.start_button.visible=False
        self.stop_button.visible=True





    # def start_stop_handler(self, e):
        
    
        

        # try:

        # try: ## TODO: can be separated into two different functions 
        #     if event.is_set(): ## TODO: event name is unclear
        #         ## TODO: put this code inside a function
        #         output.value = "" ## TODO: output what ?
        #         output.update() ## TODO: not needed
        #         event_finish_to_collect_data=True
        #         disabled_input_on_start = False ## TODO: name is not clear should be in the global files
        #         disabled_input(disabled_input_on_start, route_id, Platform_flight_index, platform_id, platform_name,
        #                     date, status_indicator_red, status_indicator_yellow, status_indicator_green) ## TODO: name should be more clear
        #         start_stop_button.text = "Start"
        #         start_stop_button.bgcolor = cl.GREEN
        #         start_stop_button.update()  ## TODO: not needed
        #         page.update()
        #         stop() ## TODO: not indicative 
        #     else:
        #         if event_finish_to_collect_data:
        #             output.value = "The system is already running"
        #             output.color = "red"
        #             output.update()
        #             return
                
        #         disabled_input_on_stop = True
        #         disabled_input(disabled_input_on_stop, route_id, Platform_flight_index, platform_id, platform_name, date,
        #                     status_indicator_red, status_indicator_yellow, status_indicator_green)
        #         start_stop_button.text = "Stop"
        #         start_stop_button.bgcolor = cl.RED
        #         start_stop_button.update()
        #         page.update()
        #         event.set() 
        #         open_socket(event, route_id.value, Platform_flight_index.value,
        #                     platform_id.value, platform_name.value, date.text, status_indicator_red,
        #                     status_indicator_yellow, status_indicator_green, status_connection,
        #                     cont_json_received, cont_send_json_to_cloud, running_problems) ## TODO: function name is not clear
        #         event_finish_to_collect_data=False
        # except Exception as e:
        #     pass

        # start_button,stop_button
            

    def set_input_disabled_status(self):

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
        )

        self.page.update()









# if __name__ == "__main__":
#     def main(page: Page):
#        GUI(page)


#     ft.app(target=main)

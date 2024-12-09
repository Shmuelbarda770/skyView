# from flet import Text, TextField, ElevatedButton, Container, colors as cl, alignment, CrossAxisAlignment
# from datetime import datetime

# class Elements:
#     def _init_(self):
#         self.date_now = datetime.now()
    
#     title = Text(
#         "Drone Management Dashboard",
#         size=30,
#         weight="bold",
#         color=cl.CYAN,
#         text_align="center"
#     )
    
    
#     route_id = TextField(
#         label="Route id",
#         bgcolor=cl.GREY_200,
#         width=250,
#         height=60,
#         fill_color="blue-light",
#         max_length=20,
#         value="ffghghfsfh",
#         hint_text="Only letters or numbers",
#         color="black",
#         text_align="center",
#         border_radius=8
#     )
#     Platform_flight_index = TextField(
#         label="Platform flight index",
#         bgcolor=cl.GREY_200,
#         width=250,
#         height=60,
#         fill_color="blue-light",
#         max_length=3,
#         value="ABC",
#         hint_text="Only uppercase letters",
#         color="black",
#         text_align="center",
#         border_radius=8
#     )
#     platform_id = TextField(
#         label="Platform id",
#         width=250,
#         bgcolor=cl.GREY_200,
#         height=60,
#         fill_color="blue-light",
#         max_length=3,
#         value="232",
#         hint_text="Only numbers",
#         color="black",
#         text_align="center",
#         border_radius=8
#     )
#     platform_name = TextField(
#         label="Platform name",
#         bgcolor=cl.GREY_200,
#         width=250,
#         height=60,
#         fill_color="blue-light",
#         max_length=3,
#         value="SDA",
#         hint_text="Only numbers",
#         color="black",
#         text_align="center",
#         border_radius=8
#     )
    
    
#     page_horizontal_alignment = CrossAxisAlignment.CENTER
    
#     def handle_change(e):
#         Elements.date.text = e.control.value.strftime("%Y-%m-%d")
#         Elements.date.update()
    

#     date = ElevatedButton(
#         "Pick Date",
#         icon="calendar_month",
#         on_click=lambda e: Elements.page.open(
#             ft.DatePicker(
#                 first_date=datetime(year=self.date_now.year, month=self.date_now.month, day=self.date_now.day),
#                 last_date=datetime(year=self.date_now.year + 15, month=self.date_now.month, day=self.date_now.day),
#                 on_change=handle_change
#             )
#         ),
#         bgcolor="#00ACC1",
#         width=250,
#         height=50
#     )
    

#     output = Text(value="", color="red")
    
#     status_indicator_red = Container(
#         width=20,
#         height=20,
#         bgcolor="red",
#         border_radius=25,
#         alignment=alignment.center,
#         visible=True
#     )
#     status_indicator_yellow = Container(
#         width=20,
#         height=20,
#         bgcolor="yellow",
#         border_radius=25,
#         alignment=alignment.center,
#         visible=False
#     )
#     status_indicator_green = Container(
#         width=20,
#         height=20,
#         bgcolor="green",
#         border_radius=25,
#         alignment=alignment.center,
#         visible=False
#     )
    
#     status_connection = Text(value="", color="white")
#     cont_json_received = Text(value="0", color="white")
#     explanation_text_cont_json_received = Text(
#         value="Count of received JSON data from the drone: ",
#         color="white"
#     )
#     cont_send_json_to_cloud = Text(value="0", color="white")
#     explanation_text_cont_send_json_to_cloud = Text(
#         value="Number of JSON sent to the cloud: ",
#         color="white"
#     )
#     running_problems = Text(value="", color="red")
#     explanation_running_problems = Text(value="Error: ", color="red")
    

#     start_stop_button = ElevatedButton(
#         text="start",
#         width=200,
#         bgcolor=cl.GREEN
#     )
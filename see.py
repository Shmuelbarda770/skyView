




# import threading
# import flet as ft
# from flet import Page, TextField, ElevatedButton, Row, Column
# from datetime import datetime
# from drone_comm_system import open_socket, stop
# from input_Validation import validate_date, validate_int, validate_string

# def main(page: Page):
   
#     page.title = "skyView"
#     page.window.width = 600
#     page.window.height = 600
#     page.vertical_alignment = "center"
#     page.horizontal_alignment = "center"

   
#     is_details_entered = False
#     thread_01_status = threading.Event()

   
#     route_id = TextField(label="Route id", width=200, height=60, fill_color='blue-light', max_length=20)
#     flight_id = TextField(label="Flight id", width=200, height=60, fill_color='blue-light', max_length=20)
#     platform_id = TextField(label="Platform id", width=200, height=60, fill_color='blue-light', max_length=3)
#     platform_name = TextField(label="Platform name", width=200, height=60, fill_color='blue-light', max_length=20)
#     date = ft.TextField(
#         label="Date",
#         value=datetime.now().strftime('%d-%m-%Y'),
#         width=200,
#         fill_color="blue-light"
#     )

    
#     submit_button = ElevatedButton(text="Submit", width=200)
#     start_stop_button = ElevatedButton(text="start", width=200, bgcolor="green")

   
#     def switch_to_start_stop(e):
#         nonlocal is_details_entered

#         route_id_value = route_id.value
#         flight_id_value = flight_id.value
#         platform_id_value = platform_id.value
#         platform_name_value = platform_name.value
#         date_value = date.value

     
#         if (not validate_string(route_id_value) or
#             not validate_string(flight_id_value) or
#             not validate_int(platform_id_value) or
#             not validate_string(platform_name_value) or
#             not validate_date(date_value)):
#             page.add(ft.Text("Please enter all fields.", color="red"))
#             page.update()
#             return

       
#         is_details_entered = True
#         update_view()

    
#     def start_stop_handler(e):
#         if thread_01_status.is_set():
#             print("stop")
#             thread_01_status.clear()
#             stop(thread_01_status)
#             start_stop_button.text = "start"
#             start_stop_button.bgcolor = "green" 
#         else:
#             print("start")
#             thread_01_status.set()
#             start_stop_button.text = "stop"
#             start_stop_button.bgcolor = "red"
#             open_socket(thread_01_status, route_id.value, flight_id.value, platform_id.value, platform_name.value, date.value)
#         start_stop_button.update()
#         page.update()

    
#     def update_view():
#         page.controls.clear()
#         if not is_details_entered:
#             page.add(
#                 Row(
#                     controls=[Column([route_id, flight_id, platform_id, platform_name, date, submit_button])],
#                     alignment=ft.MainAxisAlignment.CENTER
#                 )
#             )
#         else:
#             page.add(
#                 Row(
#                     controls=[start_stop_button],
#                     alignment=ft.MainAxisAlignment.CENTER
#                 )
#             )
#         page.update()

    
#     submit_button.on_click = switch_to_start_stop
#     start_stop_button.on_click = start_stop_handler

    
#     update_view()

# if __name__ == "__main__":
#     ft.app(target=main)



# import socket
# import threading
# import json
# import queue
# import logging
# # from json_sender import send
# import threading
# import configparser
# from logging.handlers import QueueHandler, QueueListener
# import time

# config = configparser.ConfigParser()
# config.read('config.ini')



# queue_size = config.getint('settings', 'queue_size')
# size_bytes_from_drone = config.getint('settings', 'size_bytes_from_drone')

# data_queue = queue.Queue(maxsize=queue_size)


# logging.basicConfig(level=logging.INFO, filename='test.log', filemode='w' , format='%(asctime)s - %(levelname)s - %(message)s') ## TODO: thread safe
# logger = logging.getLogger()
# log_queue = queue.Queue()
# queue_handler = QueueHandler(log_queue)
# listener = QueueListener(log_queue, *logger.handlers)
# logger.addHandler(queue_handler)
# listener.start()


# def send_data_to_cloud(thread_01_status):
#     while thread_01_status.is_set():
#         try:
#             data_from_drone = data_queue.get(block=True, timeout=60)
#             if data_from_drone:
#                 logger.info("Sending data to cloud")
#                 json.dumps(data_from_drone)
#                 # send(data_from_drone)
#             else:
#                 logger.info("Waiting for data in queue")
#             data_from_drone=None
#         except Exception as e:
#             logger.error(f"Error sending data: {e}")

#     logger.info("send_data_to_cloud thread stopped")


# def collect_data(thread_01_status, route_id , flight_id , platform_id , platform_name , date):

#     # ip = config.get('settings', 'ip')
#     # port = config.getint('settings', 'port')
#     ip = "127.0.0.1"
#     port = 3000
#     soc=None
#     soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    
#     # while True:
#             # try:
#     soc.bind((ip, port))
#     logger.info("Successfully bound to ip and port")
#                 # break
#             # except Exception as e:
#                 # logger.warning(f"Error binding to port: {e}")
#                 # time.sleep(5)
#                 # continue

#     try:    
#         while thread_01_status.is_set():

            

#             soc.listen(5) ## TODO: why 1?
#             server_socket, server_address = soc.accept() ## TODO: logger to indicate that is waiting for connection, put maximum time for connection if no connection print log and keep in a while loop. 
#             logger.info("Drone connected")
#             try:
#                 data = server_socket.recv(size_bytes_from_drone)
#                 if data:
#                     data = json.loads(data)
#                     data=upData_json(data,route_id , flight_id , platform_id , platform_name , date)

#                     print(data)
#                     logger.info("Data received and information added from the inputs")

#                 if data_queue.full():
#                     data_queue.queue.clear()
#                     logger.warning("Queue has been cleared")


                
#                 data_queue.put(data)
#             except Exception as e:
#                 logger.warning(f"{e}")
#     except Exception as e:
#         print("i")
#     finally:
#         print(server_socket)
#         if server_socket:
#             server_socket.close()## TODO: make sure that the socket is close when the thead is killed
#         soc.close()
        
    
    


# def upData_json(new_json, route_id , flight_id , platform_id , platform_name , date):
#     data={'azimuth':new_json['azimuth'],
#             'height': new_json['height'],
#             'roll': new_json['roll'],
#             'pitch': new_json['pitch'],
#             'drone_id': new_json['drone_id'],
#             'timeOfLastKnownLocation': new_json['timeOfLastKnownLocation'],
#             'coordinate': new_json['coordinate'],
#             'route_id':route_id,
#             'flight_id':flight_id,
#             'platform_id':platform_id,
#             'platform_name':platform_name,
#             'Date':date
#             }
#     return data



# def open_socket(thread_01_status,route_id , flight_id , platform_id , platform_name , date):
#     print("open_soc")
#     # soc = None
#     collector_thread = threading.Thread(target=collect_data, args=(thread_01_status,route_id , flight_id , platform_id , platform_name , date), daemon=True)
#     collector_thread.start()

#     cloud_thread = threading.Thread(target=send_data_to_cloud, args=(thread_01_status,), daemon=True)
#     cloud_thread.start()

#     collector_thread.join()
#     cloud_thread.join()




# def stop(thread_01_status):
#     logger.info("Stopping Connection")
#     thread_01_status.clear()
#     # print(threading.enumerate())
    

import socket
import threading
import json
import queue
import logging
import time
import sys
from pathlib import Path
from json_sender import send
from logging.handlers import QueueHandler, QueueListener,TimedRotatingFileHandler
import configparser
from updatePage import  light,message_view,add_num_cont_send_json_to_cloud,add_num_cont_json_received,show_error_in_screen
from validation_manager import validate_json
import datetime

event = threading.Event()



if hasattr(sys, "_MEIPASS"):
    PROJ_ROOT = Path(getattr(sys, "_MEIPASS"))
else:
    PROJ_ROOT = Path(__file__).resolve().parent

config_path = PROJ_ROOT / 'config.ini'

config = configparser.ConfigParser()
config.read(config_path)

QUEUE_SIZE  = config.getint('settings', 'QUEUE_SIZE')
SIZE_BYTES_FROM_DRONE = config.getint('settings', 'SIZE_BYTES_FROM_DRONE')

FILENAME=config.get('logRotation', 'FILENAME')
WHEN_LOG=config.get('logRotation', 'WHEN')
INTERVAL_LOG=config.getint('logRotation', 'INTERVAL')
BACKUP_COUNT=config.getint('logRotation', 'BACKUP_COUNT')

data_queue = queue.Queue(maxsize=QUEUE_SIZE)


log_queue = queue.Queue()
rotating_handler = TimedRotatingFileHandler(
    filename=FILENAME , 
    when=WHEN_LOG, 
    interval=INTERVAL_LOG,
    backupCount=BACKUP_COUNT 
)
rotating_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger()
logger.setLevel(logging.INFO)

queue_handler = QueueHandler(log_queue)
logger.addHandler(queue_handler)

listener = QueueListener(log_queue, rotating_handler, stream_handler)
listener.start()

class MessageIDGenerator:
    def __init__(self):
        self.id_for_message_id = 0 

    def get_next_id(self):
        self.id_for_message_id += 1
        return self.id_for_message_id

id_for_MessageID_obj = MessageIDGenerator()


def send_data_to_cloud(event,status_indicator_green,status_indicator_red ,status_indicator_yellow,cont_send_json_to_cloud,running_problems):
    while event.is_set():
        try:
            data_from_drone = data_queue.get(block=True, timeout=1)
            print(data_from_drone)
            if data_from_drone:
                send(data_from_drone)
                logger.info("Sending data to cloud")
                color_status="green"
                light(status_indicator_green,status_indicator_red ,status_indicator_yellow,color_status)
                add_num_cont_send_json_to_cloud(cont_send_json_to_cloud)
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            show_error_in_screen( running_problems,"Error sending data")
            if not event.is_set():
                break



def collect_data(event, route_id, Platform_flight_index, 
                            platform_id, platform_name, date, status_indicator_red,
                            status_indicator_yellow, status_indicator_green, status_connection, 
                            cont_json_received, cont_send_json_to_cloud,running_problems):

    try:
        show_error_in_screen(running_problems,"")
        message_view(status_connection, "Waiting to connect")
        try:
            
            server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except Exception as e:
            print(e)
        
        IP = config.get('settings', 'IP')
        PORT = config.getint('settings', 'PORT')
        while event.is_set():
            
            connected = False
            while not connected and event.is_set():
                try:
                    time.sleep(2)
                    server_socket.bind((IP, PORT))
                    
                    logger.info(f"Successfully bound to IP and port, the ip is:{IP} and port : {PORT}")
                    connected = True
                except Exception as e:
                    logger.error(f"Failed to bind IP and port: {e},the ip  is:{IP} and port : {PORT}")
                    show_error_in_screen( running_problems,"Failed to bind IP and port")


            SOCKET_LISTEN = config.getint('settings', 'SOCKET_LISTEN') or 1
            server_socket.listen(SOCKET_LISTEN)
            server_socket.settimeout(10)
            while event.is_set():
                
                try:
                    logger.info("Waiting for drone to connect")
                    server, address = server_socket.accept()
                    message_view(status_connection, "Connection to drone")
                    color_status="yellow"
                    light(status_indicator_green,status_indicator_red,status_indicator_yellow,color_status)
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"Error while waiting for drone connection: {e}")
                    show_error_in_screen(running_problems,"Error while waiting for drone connection")
                    continue

                
                while event.is_set() and server:

                    try:
                        data = server.recv(SIZE_BYTES_FROM_DRONE)
                        if not data:
                            break

                        logger.info(f"Data received")
                        add_num_cont_json_received(cont_json_received)
                        message_view(status_connection, 'Receives JSON from drone')
                        processed_data = upData_json(data, route_id, platform_name, platform_id, date, Platform_flight_index,running_problems)

                        if processed_data:
                            queue_status(processed_data)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        logger.error(f"Error during drone connection: {e}")
                        show_error_in_screen( running_problems,"The drone stop to send JSON")
                        break
    except RuntimeError as e:
            event.clear()
    except Exception as e:
        logger.error(f"Socket error: {e}")
        show_error_in_screen(running_problems,f"Socket error")
    finally:
        
        if server_socket:
            try:
                server_socket.close()
                logger.info("Socket closed")
            except Exception as e:
                logger.error(f"Failed to close the socket: {e}")
                show_error_in_screen(running_problems,"Failed to close the socket")


def open_socket(event: threading.Event, route_id, Platform_flight_index, 
                            platform_id, platform_name, date, status_indicator_red,
                            status_indicator_yellow, status_indicator_green, status_connection, 
                            cont_json_received, cont_send_json_to_cloud,running_problems):
    event.clear()
    event.set()
    
    try:
        tread1=threading.Thread(target= collect_data,args=( event, route_id, Platform_flight_index, 
                            platform_id, platform_name, date, status_indicator_red,
                            status_indicator_yellow, status_indicator_green, status_connection, 
                            cont_json_received, cont_send_json_to_cloud,running_problems),daemon=True)
        tread2=threading.Thread(target=send_data_to_cloud, args=(event,status_indicator_green,status_indicator_red ,status_indicator_yellow,cont_send_json_to_cloud,running_problems),daemon=True)
        
        tread1.start()
        tread2.start()

        tread1.join()
        tread2.join()

        
    except Exception as e:
        logger.error(f"Error in thread pool: {e}")
    finally:
        
        logger.info("Thread pool shut down.")
        print(len(threading.enumerate()))


def stop():

    logger.info("Stopping threads.")
    event.clear()
    while not data_queue.empty():
        data_queue.get()
    logger.info("Threads stopped.")


def upData_json(new_json,route_id, platform_name, platform_id, date,Platform_flight_index,running_problems):

    id_for_message_id = id_for_MessageID_obj.get_next_id()

    data_conversion = json.loads(new_json)
    validate_data_conversion=validate_json(data_conversion,running_problems,logger)
    conversion_date_for_flight_ID= datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
    if validate_data_conversion:
        data={
            'azimuth': data_conversion['azimuth'],
            'height': data_conversion['height'],
            'time_of_last_known_location': data_conversion['timeOfLastKnownLocation'],
            'coordinate': data_conversion['coordinate'],
            'route_id': route_id,
            'platform_flight_index': Platform_flight_index,
            'platform_id': int(platform_id),
            'platform_name': platform_name,
            'date': date,
            'message_id':id_for_message_id,
            'flight_id':f"{platform_name}{platform_id}_{conversion_date_for_flight_ID}_{Platform_flight_index}",
            'roll':0.0,
            'pitch':0.0
        }
        return data
    else:
        pass


def clear_queue():
    while not data_queue.empty():
        try:
            data_queue.get_nowait()
        except Exception as e:
            logger.error(f"Failed to clear the queue: {e}")
            

    logger.info("Queue is full and has been cleared")


def queue_status(data_to_queue):
    if data_queue.full():
        clear_queue()
                    
    data_queue.put(data_to_queue)
    logger.info("Data added to queue")
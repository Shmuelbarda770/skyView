

import socket
import threading
import json
import queue
import logging
import time
import sys
from pathlib import Path
from cloud_func.json_sender import send
from logging.handlers import QueueHandler, QueueListener,TimedRotatingFileHandler
import configparser
from concurrent.futures import ThreadPoolExecutor
from updatePage import light,message_view,add_num_cont_send_json_to_cloud,add_num_cont_json_received,show_error_in_screen
from validation.data_validation import validate_azimuth,validate_coordinate,validate_height,validate_timeOfLastKnownLocation
import datetime


if hasattr(sys, "_MEIPASS"):
    PROJ_ROOT = Path(getattr(sys, "_MEIPASS"))
else:
    PROJ_ROOT = Path(__file__).resolve().parent

config_path = PROJ_ROOT / 'config.ini'

config = configparser.ConfigParser()
config.read(config_path)

queue_size = config.getint('settings', 'queue_size')
size_bytes_from_drone = config.getint('settings', 'size_bytes_from_drone')

fileName=config.get('logRotation', 'fileName')
when_log=config.get('logRotation', 'when')
interval_log=config.getint('logRotation', 'interval')
backup_count=config.getint('logRotation', 'backup_count')

data_queue = queue.Queue(maxsize=queue_size)

server_data = {
    'server_socket': None,
    'executor': None,
    'future_collector': None,
    'future_cloud': None,
    'status_connection':None
}


log_queue = queue.Queue()
rotating_handler = TimedRotatingFileHandler(
    filename=fileName, 
    when=when_log, 
    interval=interval_log,
    backupCount=backup_count
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


def send_data_to_cloud(thread_01_status):
    while thread_01_status.is_set():
        try:
            data_from_drone = data_queue.get(block=True, timeout=1)
            print(data_from_drone)
            if data_from_drone:
                
                send(data_from_drone)
                logger.info("Sending data to cloud")
                color_status="green"
                light(server_data['status_indicator_green'],server_data['status_indicator_red'],server_data['status_indicator_yellow'],color_status)
                add_num_cont_send_json_to_cloud(server_data['cont_send_json_to_cloud'])
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            show_error_in_screen( server_data['running_problems'],"Error sending data")
            if not thread_01_status.is_set():
                break
    logger.info("Cloud thread stopped")



def collect_data(thread_01_status, route_id, Platform_flight_index, platform_id, platform_name, date):

    try:
        
        show_error_in_screen( server_data['running_problems'],"")
        message_view(server_data['status_connection'], "Waiting to connect")
        server_data['server_socket'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        while thread_01_status.is_set():
            ip = config.get('settings', 'ip')
            port = config.getint('settings', 'port')

            connected = False
            while not connected and thread_01_status.is_set():
                try:
                    server_data['server_socket'].bind((ip, port))
                    logger.info(f"Successfully bound to IP and port, the ip is:{ip} and port : {port}")
                    connected = True
                except Exception as e:
                    logger.error(f"Failed to bind IP and port: {e},the ip  is:{ip} and port : {port}")
                    show_error_in_screen( server_data['running_problems'],"Failed to bind IP and port")

            socket_listen= config.getint('settings', 'socket_listen') or 1
            server_data['server_socket'].listen(socket_listen)
            while thread_01_status.is_set():
                try:
                    
                    logger.info("Waiting for drone to connect")
                    server, address = server_data['server_socket'].accept()
                    message_view(server_data['status_connection'], "Connection to drone")
                    color_status="yellow"
                    light(server_data['status_indicator_green'],server_data['status_indicator_red'],server_data['status_indicator_yellow'],color_status)
                except Exception as e:
                    logger.error(f"Error while waiting for drone connection: {e}")
                    show_error_in_screen( server_data['running_problems'],"Error while waiting for drone connection")
                    continue

                
                while thread_01_status.is_set() and server:
                    try:
                        data = server.recv(size_bytes_from_drone)
                        
                        if not data:
                            break

                        logger.info(f"Data received")
                        add_num_cont_json_received(server_data['cont_json_received'])
                        message_view(server_data['status_connection'], 'Receives JSON from drone')
                        
                        processed_data = upData_json(data, route_id, platform_name, platform_id, date, Platform_flight_index)
                        
                        if processed_data:
                            queue_status(processed_data)
                    except Exception as e:
                        logger.error(f"Error during drone connection: {e}")
                        show_error_in_screen( server_data['running_problems'],"The drone stop to send JSON")
                        if not thread_01_status.is_set():
                            break
                        time.sleep(1)


    except Exception as e:
        logger.error(f"Socket error: {e}")
        show_error_in_screen( server_data['running_problems'],f"Socket error")
        
    finally:
        if server_data['server_socket']:
            try:
                server_data['server_socket'].close()
                logger.info("Socket closed")
            except Exception as e:
                logger.error(f"Failed to close the socket: {e}")
                show_error_in_screen( server_data['running_problems'],"Failed to close the socket")



def open_socket(thread_01_status, route_id, Platform_flight_index, platform_id,
                 platform_name, date_for_json,status_indicator_red,status_indicator_yellow,
                 status_indicator_green,status_connection,cont_json_received,cont_send_json_to_cloud,running_problems):
    
    server_data['status_indicator_red']=status_indicator_red
    server_data['status_indicator_yellow']=status_indicator_yellow
    server_data['status_indicator_green']=status_indicator_green
    server_data['status_connection']=status_connection
    server_data['cont_json_received']=cont_json_received
    server_data['cont_send_json_to_cloud']=cont_send_json_to_cloud
    server_data['running_problems']=running_problems

    stop(thread_01_status,status_connection,running_problems,False)
    
    thread_01_status.clear()
    thread_01_status.set()

    if server_data['executor'] is None or server_data['executor']._shutdown:
        server_data['executor'] = ThreadPoolExecutor(max_workers=2)

    server_data['future_collector'] = server_data['executor'].submit(collect_data, thread_01_status, route_id, Platform_flight_index, platform_id, platform_name, date_for_json)
    server_data['future_cloud'] =server_data['executor'].submit(send_data_to_cloud, thread_01_status)
    # with ThreadPoolExecutor(max_workers=3) as executor:
    #     server_data['future_collector'] = executor.submit(collect_data, thread_01_status, route_id, Platform_flight_index, platform_id, platform_name, date_for_json)
    #     server_data['future_cloud'] =executor.submit(send_data_to_cloud, thread_01_status)

    
   
    
    


def stop(thread_01_status,status_connection,running_problems,show=True):

    logger.info("Stopping connection")
    thread_01_status.clear()
    clear_queue()

    if server_data['server_socket']:
        try:
            server_data['server_socket'].close()
            server_data['server_socket'] = None
            logger.info("close connection to the drone")
        except:
            show_error_in_screen( running_problems,"Failed to close the socket")
    
    if server_data['executor']:
        if server_data['future_collector']:
            server_data['future_collector'].cancel()
        if server_data['future_cloud']:
            server_data['future_cloud'].cancel()
        
        if server_data['executor']:
            server_data['executor'].shutdown(wait=True, cancel_futures=True)
            server_data['executor'] = None
    
    server_data['future_collector'] = None
    server_data['future_cloud'] = None
    

    if show:
        message_view(status_connection,'Stopping connection')
    print(f"Remaining active threads: {threading.active_count()}")
    

def queue_status(data_to_queue):
    if data_queue.full():
        clear_queue()
                  
    data_queue.put(data_to_queue)
    logger.info("Data added to queue")


def upData_json(new_json,route_id, platform_name, platform_id, date,Platform_flight_index):
    id_for_message_id = id_for_MessageID_obj.get_next_id()
    data_conversion = json.loads(new_json)

    validate_data_conversion=validate_json(data_conversion)
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


def validate_json(data_conversion):
    try:
        if validate_azimuth(data_conversion['azimuth']) and validate_coordinate(data_conversion['coordinate']) and validate_height(data_conversion['height']) and validate_timeOfLastKnownLocation(data_conversion['timeOfLastKnownLocation']):
            return True
        return False
    except Exception as e:
        show_error_in_screen( server_data['running_problems'],"Problem with validate json")
        logger.warning(f'Problem with validate json, and the error is:{e},the data is: {data_conversion}')


def clear_queue():


    while not data_queue.empty():
        try:
            data_queue.get_nowait()
        except Exception as e:
            logger.error(f"Failed to clear the queue: {e}")
            
    logger.info("Queue is full and has been cleared")

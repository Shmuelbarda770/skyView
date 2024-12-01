import socket
import threading
import json
import queue
import logging
import time
import sys
from pathlib import Path

from json_sender import send 
from logging.handlers import QueueHandler, QueueListener
import configparser
from concurrent.futures import ThreadPoolExecutor

from updatePage import blink_light,message_view,add_num_cont_send_json_to_cloud,add_num_cont_json_received
from data_validation import validate_azimuth,validate_coordinate,validate_height,validate_timeOfLastKnownLocation


if hasattr(sys, "_MEIPASS"):
    PROJ_ROOT = Path(getattr(sys, "_MEIPASS"))
else:
    PROJ_ROOT = Path(__file__).resolve().parent

config_path = PROJ_ROOT / 'config.ini'

config = configparser.ConfigParser()
config.read(config_path)

queue_size = config.getint('settings', 'queue_size')
size_bytes_from_drone = config.getint('settings', 'size_bytes_from_drone')

data_queue = queue.Queue(maxsize=queue_size)

server_data = {
    'server_socket': None,
    'executor': None,
    'future_collector': None,
    'future_cloud': None,
    'status_connection':None
}


logging.basicConfig(level=logging.INFO, filename='test.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)


stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


listener = QueueListener(log_queue, *logger.handlers)
logger.addHandler(queue_handler)

listener.start()


def send_data_to_cloud(thread_01_status):
    while thread_01_status.is_set():
        try:
            data_from_drone = data_queue.get(block=True, timeout=1)
            print(data_from_drone)
            if data_from_drone:
                logger.info("Sending data to cloud")
                data=json.dumps(data_from_drone)
                print(data)
                # send(data)
                add_num_cont_send_json_to_cloud(server_data['cont_send_json_to_cloud'])
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            if not thread_01_status.is_set():
                break
    logger.info("Cloud thread stopped")




def collect_data(thread_01_status, route_id, Platform_flight_index, platform_id, platform_name, date):
    try:
        message_view(server_data['status_connection'], "Waiting to connect")
        server_data['server_socket'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while thread_01_status.is_set():
            ip = config.get('settings', 'ip')
            port = config.getint('settings', 'port')

            
            connected = False
            while not connected and thread_01_status.is_set():
                try:
                    server_data['server_socket'].bind((ip, port))
                    logger.info("Successfully bound to IP and port")
                    connected = True
                except Exception as e:
                    logger.error(f"Failed to bind IP and port: {e}. Retrying...")
                    time.sleep(1) 

            server_data['server_socket'].listen(1)

            while thread_01_status.is_set():
                try:
                    logger.info("Waiting for drone to connect")
                    server, address = server_data['server_socket'].accept()
                    message_view(server_data['status_connection'], "Connection to drone")
                except Exception as e:
                    logger.error(f"Error while waiting for drone connection: {e}")
                    continue

                
                while thread_01_status.is_set() and server:
                    try:
                        data = server.recv(size_bytes_from_drone)
                        print(data)
                        
                        logger.info(f"Data received: {data}")
                        add_num_cont_json_received(server_data['cont_json_received'])
                        message_view(server_data['status_connection'], 'Receives JSON from drone')

                        processed_data = upData_json(data, route_id, platform_name, platform_id, date, Platform_flight_index)
                        print(processed_data)
                        if processed_data:
                            queue_status(processed_data)
                    except Exception as e:
                        logger.error(f"Error during drone connection: {e}")
                        continue

    except Exception as e:
        logger.error(f"Socket error: {e}")
    finally:
        if server_data['server_socket']:
            try:
                server_data['server_socket'].close()
                logger.info("Socket closed")
            except Exception as e:
                logger.error(f"Failed to close the socket: {e}")



def open_socket(thread_01_status, route_id, Platform_flight_index, platform_id,
                 platform_name, date_for_json,status_indicator_red,status_indicator_yellow,
                 status_indicator_green,status_connection,cont_json_received,cont_send_json_to_cloud):

    server_data['status_indicator_yellow']=status_indicator_yellow
    server_data['status_indicator_green']=status_indicator_green
    server_data['status_connection']=status_connection
    server_data['cont_json_received']=cont_json_received
    server_data['cont_send_json_to_cloud']=cont_send_json_to_cloud

    

    stop(thread_01_status,server_data['status_connection'],status_indicator_red,False,False)
    
    thread_01_status.clear()
    thread_01_status.set()
    
    if server_data['executor'] is None or server_data['executor']._shutdown:
        server_data['executor'] = ThreadPoolExecutor(max_workers=2)
    
    server_data['future_collector'] = server_data['executor'].submit(collect_data, thread_01_status, route_id, Platform_flight_index, platform_id, platform_name, date_for_json)
    server_data['future_cloud'] = server_data['executor'].submit(send_data_to_cloud, thread_01_status)
    


def stop(thread_01_status,status_indicator_red,status_connection,light=True,show=True,):

    logger.info("Stopping connection")
    thread_01_status.clear()
    
    if server_data['server_socket']:
        try:
            server_data['server_socket'].close()
            server_data['server_socket'] = None
            logger.info("close connection to the drone")
        except:
            pass
    
    if server_data['executor']:
        if server_data['future_collector']:
            server_data['future_collector'].cancel()
        if server_data['future_cloud']:
            server_data['future_cloud'].cancel()
        
        server_data['executor'].shutdown(wait=True, cancel_futures=True)
        server_data['executor'] = None
    
    server_data['future_collector'] = None
    server_data['future_cloud'] = None
    
    clear_queue()
    if show:
        message_view(status_connection,'Stopping connection')
    if light:
        blink_light(status_indicator_red, "red", "transparent")
    print(f"Remaining active threads: {threading.active_count()}")
    

def queue_status(data_to_queue):
    if data_queue.full():
        clear_queue()
                    
    data_queue.put(data_to_queue)
    logger.info("Data added to queue")


def upData_json(new_json,route_id, platform_name, platform_id, date,Platform_flight_index):
    data_conversion = json.loads(new_json)

    validate_data_conversion=validate_json(data_conversion)
    
    if validate_data_conversion:
        data={
            'azimuth': data_conversion['azimuth'],
            'height': data_conversion['height'],
            'drone_id': data_conversion['droneId'],
            'timeOfLastKnownLocation': data_conversion['timeOfLastKnownLocation'],
            'coordinate': data_conversion['coordinate'],
            'route_id': route_id,
            'Platform_flight_index': Platform_flight_index,
            'platform_id': platform_id,
            'platform_name': platform_name,
            'Date': date,
            'messageId':"",
            'flight_ID':""
            
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
        
        logger.warning(f'Problem with validate json, and the error is:{e},the data is: {data_conversion}')


def clear_queue():
    while not data_queue.empty():
        try:
            data_queue.get_nowait()
        except Exception as e:
            logger.error(f"Failed to clear the queue: {e}")

    logger.info("Queue is full and has been cleared")

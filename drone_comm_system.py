import socket
import threading
import json
import queue
import logging
import time
from json_sender import send 
from logging.handlers import QueueHandler, QueueListener
import configparser
from concurrent.futures import ThreadPoolExecutor

from updatePage import blink_light,message_view,add_num_cont_send_json_to_cloud,add_num_cont_json_received
from data_validation import validate_azimuth,validate_coordinate,validate_height,validate_pitch,validate_roll,validate_timeOfLastKnownLocation

config = configparser.ConfigParser()
config.read('config.ini')

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


logging.basicConfig(level=logging.INFO, filename='test.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)
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
        message_view(server_data['status_connection'],"Waiting to connect")
        server_data['server_socket'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # server_data['server_socket'].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ip=config.get('settings','ip')
        port=config.getint('settings','port')

        try:
            server_data['server_socket'].bind(("127.0.0.1", 3000))
            logger.info("Successfully bound to ip and port")
        except Exception as e:
            logger.info(f"Failed to bind IP and port and the error is: {e}")
        
        server_data['server_socket'].listen(1)
        server_data['server_socket'].settimeout(1)
        
        while thread_01_status.is_set():
            try:
                server, address = server_data['server_socket'].accept()
                logger.info("Drone connected")
                message_view(server_data['status_connection'],"Connection to drone")
                # blink_light(server_data['status_indicator_yellow'], "yellow", "transparent")
                while thread_01_status.is_set():
                    data = server.recv(size_bytes_from_drone)

                    add_num_cont_json_received(server_data['cont_json_received'])
                    # blink_light(server_data['status_indicator_green'], "green", "transparent")
                    message_view(server_data['status_connection'],'receives json from drone')
                    data = upData_json(data,route_id, platform_name, platform_id, date,Platform_flight_index)
                    
                    queue_status(data)
                    
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Failed to connect to drone and the error is: {e}")
                if not thread_01_status.is_set():
                    break
                time.sleep(1)
                
    except Exception as e:
        logger.error(f"Socket error: {e}")
    finally:
        if server_data['server_socket']:
            try:
                server_data['server_socket'].close()
                server_data['server_socket'] = None
            except Exception as e:
                logger.error(f"Failed to close the connection with the drone, and the error is: {e}")


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
    print("d")
    if data_queue.full():
        clear_queue()
                    
    data_queue.put(data_to_queue)
    logger.info("Data added to queue")


def upData_json(new_json,route_id, platform_name, platform_id, date,Platform_flight_index):
    data_conversion = json.loads(new_json)
    print(data_conversion)
    validate_data_conversion=validate_json(data_conversion)
    print(validate_data_conversion)
    if validate_data_conversion:
        data={
            'azimuth': data_conversion['azimuth'],
            'height': data_conversion['height'],
            'roll': data_conversion['roll'],
            'pitch': data_conversion['pitch'],
            'drone_id': data_conversion['drone_id'],
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
        if validate_azimuth(data_conversion['azimuth']) and validate_coordinate(data_conversion['coordinate']) and validate_height(data_conversion['height']) and validate_pitch(data_conversion['pitch']) and validate_roll(data_conversion['roll']) and validate_timeOfLastKnownLocation(data_conversion['timeOfLastKnownLocation']):
            return True
        return False
    except Exception as e:
        logger.warning(f'Problem with validate json, and the error is:{e}')


def clear_queue():
    while not data_queue.empty():
        try:
            data_queue.get_nowait()
        except Exception as e:
            logger.error(f"Failed to clear the queue: {e}")

    logger.info("Queue is full and has been cleared")


        
































# import socket
# import threading
# import json
# import queue
# import logging
# import time
# from json_sender import send 
# from logging.handlers import QueueHandler, QueueListener
# import configparser
# from concurrent.futures import ThreadPoolExecutor


# config = configparser.ConfigParser()
# config.read('config.ini')

# queue_size = config.getint('settings', 'queue_size')
# size_bytes_from_drone = config.getint('settings', 'size_bytes_from_drone')


# data_queue = queue.Queue(maxsize=queue_size)

# server_socket = None
# executor = None
# future_collector = None
# future_cloud = None


# logging.basicConfig(level=logging.INFO, filename='test.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger()
# log_queue = queue.Queue()
# queue_handler = QueueHandler(log_queue)
# listener = QueueListener(log_queue, *logger.handlers)
# logger.addHandler(queue_handler)
# listener.start()

# def send_data_to_cloud(thread_01_status):
#     logger.info("Cloud thread started")
#     while thread_01_status.is_set():
#         try:
#             data_from_drone = data_queue.get(block=True, timeout=1)
#             if data_from_drone:
#                 logger.info("Sending data to cloud")
#                 data=json.dumps(data_from_drone)
#                 # send(data)
#         except queue.Empty:
#             continue
#         except Exception as e:
#             logger.error(f"Error sending data: {e}")
#             if not thread_01_status.is_set():
#                 break
#     logger.info("Cloud thread stopped")

# def collect_data(thread_01_status, route_id, flight_id, platform_id, platform_name, date):
#     global server_socket
#     logger.info("Collector thread started")
    
#     try:
#         server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         server_socket.bind(("127.0.0.1", 3000))
#         server_socket.listen(1)
#         server_socket.settimeout(1)
        
#         while thread_01_status.is_set():
#             try:
                
#                 server, address = server_socket.accept()
#                 logger.info("Drone connected")
                
#                 while thread_01_status.is_set():
#                     data = server.recv(size_bytes_from_drone)
                    
#                     data = json.loads(data)
#                     data = upData_json(data, route_id, flight_id, platform_id, platform_name, date)
                    
#                     if data_queue.full():
#                         data_queue.queue.clear()
                    
#                     data_queue.put(data)
                    
#             except socket.timeout:
#                 continue
#             except Exception as e:
#                 logger.error(f"Collection error: {e}")
#                 if not thread_01_status.is_set():
#                     break
#                 time.sleep(1)
                
#     except Exception as e:
#         logger.error(f"Socket error: {e}")
#     finally:
#         if server_socket:
#             try:
#                 server_socket.close()
#                 server_socket = None
#             except:
#                 pass
#         logger.info("Collector thread stopped")

# def upData_json(new_json, route_id, flight_id, platform_id, platform_name, date):
#     return {
#         'azimuth': new_json['azimuth'],
#         'height': new_json['height'],
#         'roll': new_json['roll'],
#         'pitch': new_json['pitch'],
#         'drone_id': new_json['drone_id'],
#         'timeOfLastKnownLocation': new_json['timeOfLastKnownLocation'],
#         'coordinate': new_json['coordinate'],
#         'route_id': route_id,
#         'flight_id': flight_id,
#         'platform_id': platform_id,
#         'platform_name': platform_name,
#         'Date': date
#     }

# def open_socket(thread_01_status, route_id, flight_id, platform_id, platform_name, date,):
#     global executor, future_collector, future_cloud
    
#     stop(thread_01_status,server_socket,executor,future_collector,future_cloud)
    
#     thread_01_status.clear()
#     thread_01_status.set()
    
#     if executor is None or executor._shutdown:
#         executor = ThreadPoolExecutor(max_workers=2)
    
#     future_collector = executor.submit(collect_data, thread_01_status, route_id, flight_id, platform_id, platform_name, date)
#     future_cloud = executor.submit(send_data_to_cloud, thread_01_status)
    
#     logger.info(f"Active threads: {threading.active_count()}")
#     for t in threading.enumerate():
#         logger.info(f"Thread name: {t.name}")


# def stop(thread_01_status):
#     global executor, future_collector, future_cloud, server_socket
    
#     logger.info("Stopping Connection")
#     thread_01_status.clear()
    
#     if server_socket:
#         try:
#             server_socket.close()
#             server_socket = None
#         except:
#             pass
    
#     if executor:
#         if future_collector:
#             future_collector.cancel()
#         if future_cloud:
#             future_cloud.cancel()
        
#         executor.shutdown(wait=True, cancel_futures=True)
#         executor = None
    
#     future_collector = None
#     future_cloud = None
    
#     while not data_queue.empty():
#         try:
#             data_queue.get_nowait()
#         except:
#             pass
    
#     logger.info(f"Remaining active threads: {threading.active_count()}")
#     print(f"Remaining active threads: {threading.active_count()}")
#     for t in threading.enumerate():
#         logger.info(f"Thread name: {t.name}")


# shmuel
# server_socket,executor,future_collector,future_cloud


# import socket
# import threading
# import json
# import queue
# import logging
# from json_sender import send
# import threading
# import time
# import configparser
# from logging.handlers import QueueHandler, QueueListener
# import configparser
# from concurrent.futures import ThreadPoolExecutor


# config = configparser.ConfigParser()
# config.read('config.ini')

# queue_size = config.getint('settings', 'queue_size')
# size_bytes_from_drone = config.getint('settings', 'size_bytes_from_drone')

# data_queue = queue.Queue(maxsize=queue_size)


# logging.basicConfig(level=logging.INFO, filename='test.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger()
# log_queue = queue.Queue()
# queue_handler = QueueHandler(log_queue)
# listener = QueueListener(log_queue, *logger.handlers)
# logger.addHandler(queue_handler)
# listener.start()

# def send_data_to_cloud(thread_01_status):
#     logger.info("Cloud thread started")
#     while thread_01_status.is_set():
#         try:
#             data_from_drone = data_queue.get(block=True, timeout=60)
#             if data_from_drone:
#                 logger.info("Sending data to cloud")
#                 data_from_drone=json.dumps(data_from_drone)
#                 send(data_from_drone)
#         except queue.Empty:
#             continue
#         except Exception as e:
#             logger.error(f"Error sending data: {e}")
#             if not thread_01_status.is_set():
#                 break
#     logger.info("Cloud thread stopped")


# def collect_data(thread_01_status, route_id, flight_id, platform_id, platform_name, date):
#     global server_socket
#     logger.info("Collector thread started")
    
#     try:
#         server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         server_socket.bind(("127.0.0.1", 3000))
#         server_socket.listen(1)
#         server_socket.settimeout(1)
        
#         while thread_01_status.is_set():
#             try:
#                 client, addr = server_socket.accept()
#                 logger.info("Drone connected")
                
#                 while thread_01_status.is_set():
#                     data = client.recv(size_bytes_from_drone)
#                     if not data:
#                         break
                    
#                     data = json.loads(data)
#                     data = upData_json(data, route_id, flight_id, platform_id, platform_name, date)
                    
#                     if data_queue.full():
#                         data_queue.queue.clear()
                    
#                     data_queue.put(data)
                    
#             except socket.timeout:
#                 continue
#             except Exception as e:
#                 logger.error(f"Collection error: {e}")
#                 if not thread_01_status.is_set():
#                     break
#                 time.sleep(1)
                
#     except Exception as e:
#         logger.error(f"Socket error: {e}")
#     finally:
#         if server_socket:
#             try:
#                 server_socket.close()
#                 server_socket = None
#             except:
#                 pass
#         logger.info("Collector thread stopped")


# def upData_json(new_json, route_id, flight_id, platform_id, platform_name, date):
#     return {
#         'azimuth': new_json['azimuth'],
#         'height': new_json['height'],
#         'roll': new_json['roll'],
#         'pitch': new_json['pitch'],
#         'drone_id': new_json['drone_id'],
#         'timeOfLastKnownLocation': new_json['timeOfLastKnownLocation'],
#         'coordinate': new_json['coordinate'],
#         'route_id': route_id,
#         'flight_id': flight_id,
#         'platform_id': platform_id,
#         'platform_name': platform_name,
#         'Date': date
#     }

# def open_socket(thread_01_status, route_id, flight_id, platform_id, platform_name, date):
#     global executor, future_collector, future_cloud
    
    
#     stop(thread_01_status)
    
   
#     thread_01_status.clear()
#     thread_01_status.set()
    
   
#     if executor is None or executor._shutdown:
#         executor = ThreadPoolExecutor(max_workers=2)
    
    
#     future_collector = executor.submit(collect_data, thread_01_status, route_id, flight_id, platform_id, platform_name, date)
#     future_cloud = executor.submit(send_data_to_cloud, thread_01_status)
    
#     logger.info(f"Active threads: {threading.active_count()}")
#     for t in threading.enumerate():
#         logger.info(f"Thread name: {t.name}")

# def stop(thread_01_status):
#     global executor, future_collector, future_cloud, server_socket
    
#     logger.info("Stopping Connection")
#     thread_01_status.clear()
    
    
#     if server_socket:
#         try:
#             server_socket.close()
#             server_socket = None
#         except:
#             pass
    
#     if executor:
#         if future_collector:
#             future_collector.cancel()
#         if future_cloud:
#             future_cloud.cancel()
        
#         executor.shutdown(wait=True, cancel_futures=True)
#         executor = None
    
#     future_collector = None
#     future_cloud = None
    
#     while not data_queue.empty():
#         try:
#             data_queue.get_nowait()
#         except:
#             pass
    
#     logger.info(f"Remaining active threads: {threading.active_count()}")
#     print(f"Remaining active threads: {threading.active_count()}")
#     for t in threading.enumerate():
#         logger.info(f"Thread name: {t.name}")

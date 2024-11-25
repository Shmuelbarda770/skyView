
import socket
import threading
import json
import queue
import logging
from json_sender import send
import threading
import configparser
from logging.handlers import QueueHandler, QueueListener
import configparser
from concurrent.futures import ThreadPoolExecutor


config = configparser.ConfigParser()
config.read('config.ini')

queue_size = config.getint('settings', 'queue_size')
size_bytes_from_drone = config.getint('settings', 'size_bytes_from_drone')

data_queue = queue.Queue(maxsize=queue_size)


logging.basicConfig(level=logging.INFO, filename='test.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)
listener = QueueListener(log_queue, *logger.handlers)
logger.addHandler(queue_handler)
listener.start()

def send_data_to_cloud(thread_01_status):
    logger.info("Cloud thread started")
    while thread_01_status.is_set():
        try:
            data_from_drone = data_queue.get(block=True, timeout=60)
            if data_from_drone:
                logger.info("Sending data to cloud")
                data_from_drone=json.dumps(data_from_drone)
                send(data_from_drone)
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            if not thread_01_status.is_set():
                break
    logger.info("Cloud thread stopped")


def collect_data(thread_01_status, route_id, flight_id, platform_id, platform_name, date):
    global server_socket
    logger.info("Collector thread started")
    
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("127.0.0.1", 3000))
        server_socket.listen(1)
        server_socket.settimeout(1)
        
        while thread_01_status.is_set():
            try:
                client, addr = server_socket.accept()
                logger.info("Drone connected")
                
                while thread_01_status.is_set():
                    data = client.recv(size_bytes_from_drone)
                    if not data:
                        break
                    
                    data = json.loads(data)
                    data = upData_json(data, route_id, flight_id, platform_id, platform_name, date)
                    
                    if data_queue.full():
                        data_queue.queue.clear()
                    
                    data_queue.put(data)
                    
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Collection error: {e}")
                if not thread_01_status.is_set():
                    break
                time.sleep(1)
                
    except Exception as e:
        logger.error(f"Socket error: {e}")
    finally:
        if server_socket:
            try:
                server_socket.close()
                server_socket = None
            except:
                pass
        logger.info("Collector thread stopped")


def upData_json(new_json, route_id, flight_id, platform_id, platform_name, date):
    return {
        'azimuth': new_json['azimuth'],
        'height': new_json['height'],
        'roll': new_json['roll'],
        'pitch': new_json['pitch'],
        'drone_id': new_json['drone_id'],
        'timeOfLastKnownLocation': new_json['timeOfLastKnownLocation'],
        'coordinate': new_json['coordinate'],
        'route_id': route_id,
        'flight_id': flight_id,
        'platform_id': platform_id,
        'platform_name': platform_name,
        'Date': date
    }

def open_socket(thread_01_status, route_id, flight_id, platform_id, platform_name, date):
    global executor, future_collector, future_cloud
    
    
    stop(thread_01_status)
    
   
    thread_01_status.clear()
    thread_01_status.set()
    
   
    if executor is None or executor._shutdown:
        executor = ThreadPoolExecutor(max_workers=2)
    
    
    future_collector = executor.submit(collect_data, thread_01_status, route_id, flight_id, platform_id, platform_name, date)
    future_cloud = executor.submit(send_data_to_cloud, thread_01_status)
    
    logger.info(f"Active threads: {threading.active_count()}")
    for t in threading.enumerate():
        logger.info(f"Thread name: {t.name}")

def stop(thread_01_status):
    global executor, future_collector, future_cloud, server_socket
    
    logger.info("Stopping Connection")
    thread_01_status.clear()
    
    
    if server_socket:
        try:
            server_socket.close()
            server_socket = None
        except:
            pass
    
    if executor:
        if future_collector:
            future_collector.cancel()
        if future_cloud:
            future_cloud.cancel()
        
        executor.shutdown(wait=True, cancel_futures=True)
        executor = None
    
    future_collector = None
    future_cloud = None
    
    while not data_queue.empty():
        try:
            data_queue.get_nowait()
        except:
            pass
    
    logger.info(f"Remaining active threads: {threading.active_count()}")
    print(f"Remaining active threads: {threading.active_count()}")
    for t in threading.enumerate():
        logger.info(f"Thread name: {t.name}")

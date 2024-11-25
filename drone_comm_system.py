
import socket
import threading
import json
import queue
import logging
#from json_sender import send
import threading
import configparser
from logging.handlers import QueueHandler, QueueListener

config = configparser.ConfigParser()
config.read('config.ini')



queue_size = config.getint('settings', 'queue_size')
size_bytes_from_drone = config.getint('settings', 'size_bytes_from_drone')

data_queue = queue.Queue(maxsize=queue_size)




logging.basicConfig(level=logging.INFO, filename='test.log', filemode='w' , format='%(asctime)s - %(levelname)s - %(message)s') ## TODO: thread safe
logger = logging.getLogger()
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)
listener = QueueListener(log_queue, *logger.handlers)
logger.addHandler(queue_handler)
listener.start()


def send_data_to_cloud(thread_01_status):

    while thread_01_status.is_set():
        try:
            data_from_drone = data_queue.get(block=True, timeout=60)
            if data_from_drone:
                logger.info("Sending data to cloud")
                json.dumps(data_from_drone)
                # send(data_from_drone)
            else:
                logger.info("Waiting for data in queue")
            data_from_drone=None
        except Exception as e:
            logger.error(f"Error sending data: {e}")
        

    logger.info("send_data_to_cloud thread stopped")


def collect_data(thread_01_status, soc, route_id , flight_id , platform_id , platform_name , date):

    # ip = config.get('settings', 'ip')
    # port = config.getint('settings', 'port')
    ip = "127.0.0.1"
    port = 3000

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        soc.bind((ip, port))
        logger.info("Successfully bound to ip and port")
    except Exception as e:
        logger.error("Failed to bind socket to ip and port")
        return

    soc.listen(5) ## TODO: why 1?
    server_socket, server_address = soc.accept() ## TODO: logger to indicate that is waiting for connection, put maximum time for connection if no connection print log and keep in a while loop. 
    logger.info("Drone connected")


    while thread_01_status.is_set():
        try:
            data = server_socket.recv(size_bytes_from_drone)
            if data:
                data = json.loads(data)

                

                data["route_id"]=route_id
                data["flight_id"]=flight_id
                data["platform_id"]=platform_id
                data["platform_name"]=platform_name
                data["Date"]=date
                print(data)
                logger.info("Data received and information added from the inputs")

            if data_queue.full():
                data_queue.queue.clear()
                logger.warning("Queue has been cleared")


            
            data_queue.put(data)
        except Exception as e:
            logger.warning(f"{e}")
        

    server_socket.close()## TODO: make sure that the socket is close when the thead is killed


def open_socket(thread_01_status,route_id , flight_id , platform_id , platform_name , date):
    print("open_soc")
    soc = None
    collector_thread = threading.Thread(target=collect_data, args=(thread_01_status, soc,route_id , flight_id , platform_id , platform_name , date), daemon=True)
    collector_thread.start()

    cloud_thread = threading.Thread(target=send_data_to_cloud, args=(thread_01_status,), daemon=True)
    cloud_thread.start()

    collector_thread.join()
    cloud_thread.join()




def stop(thread_01_status):
    logger.info("Stopping Connection")
    thread_01_status.clear()
    print(threading.enumerate())
    

import socket
import threading
import json
import queue
import logging
from json_sender import send
import configparser
from logging.handlers import QueueHandler, QueueListener

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

queue_size = config.getint('settings', 'queue_size')
size_bytes_from_drone = config.getint('settings', 'size_bytes_from_drone')

data_queue = queue.Queue(maxsize=queue_size)

# Setup logging with thread safety
logging.basicConfig(level=logging.INFO, filename='test.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
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
        except queue.Empty:
            logger.warning("Queue timeout: No data received to send")
        except Exception as e:
            logger.error(f"Error sending data: {e}")
    logger.info("send_data_to_cloud thread stopped")


def collect_data(thread_01_status, soc, route_id, flight_id, platform_id, platform_name, date):
    ip = "127.0.0.1"
    port = 3000

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        soc.bind((ip, port))
        logger.info("Successfully bound to IP and port")
    except Exception as e:
        logger.error(f"Failed to bind socket to IP and port: {e}")
        return

    soc.listen(5)  # Allow up to 5 simultaneous connections
    soc.settimeout(10)  # Timeout for accepting connections
    try:
        server_socket, server_address = soc.accept()
        logger.info("Drone connected")
    except socket.timeout:
        logger.warning("No connection received within timeout period")
        return

    with server_socket:
        while thread_01_status.is_set():
            try:
                data = server_socket.recv(size_bytes_from_drone)
                if data:
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        logger.error("Received invalid JSON data")
                        continue

                    # Add metadata to the received data
                    data.update({
                        "route_id": route_id,
                        "flight_id": flight_id,
                        "platform_id": platform_id,
                        "platform_name": platform_name,
                        "Date": date
                    })
                    logger.info("Data received and enriched with metadata")

                if data_queue.full():
                    data_queue.get_nowait()  # Remove the oldest item to make room
                    logger.warning("Queue was full; oldest item removed")

                data_queue.put(data)
            except socket.error as e:
                logger.warning(f"Socket error: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error: {e}")

    logger.info("Socket closed after thread termination")


def open_socket(thread_01_status, route_id, flight_id, platform_id, platform_name, date):
    soc = None
    threads = []

    collector_thread = threading.Thread(
        target=collect_data,
        args=(thread_01_status, soc, route_id, flight_id, platform_id, platform_name, date),
        daemon=True
    )
    threads.append(collector_thread)
    collector_thread.start()

    cloud_thread = threading.Thread(
        target=send_data_to_cloud,
        args=(thread_01_status,),
        daemon=True
    )
    threads.append(cloud_thread)
    cloud_thread.start()

    for thread in threads:
        thread.join()


def stop(thread_01_status):
    logger.info("Stopping Connection")
    thread_01_status.clear()

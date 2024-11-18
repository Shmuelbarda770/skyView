import socket
import threading
import json
import requests
import queue
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


data_queue = queue.Queue()


CLOUD_URL = ""


def send_data_to_cloud():
    while True:
        try:
           
            data = data_queue.get(block=True)
           
            data_dict = json.dumps({"key": "value", "data": data})
           
            response = requests.post(CLOUD_URL, json=data_dict)
            if response.status_code == 200:
                logger.info("Data sent successfully.")
            else:
                logger.warning(f"Failed to upload data to the cloud. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending data: {e}")


def collect_data():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p = '127.0.0.1' 
    port = 3000     
    soc.bind((p, port))
    soc.listen(1) 

    logger.info("Server is listening... Waiting for connection.")
    client_socket, client_address = soc.accept()
    logger.info(f"Client connected: {client_address}")

    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        logger.info(f"Received data: {data.decode()}")
      
        data_queue.put(data.decode())

    client_socket.close()  


def open_socket():
   
    collector_thread = threading.Thread(target=collect_data, daemon=True)
    collector_thread.start()

    cloud_thread = threading.Thread(target=send_data_to_cloud, daemon=True)
    cloud_thread.start()

    collector_thread.join()
    cloud_thread.join()


def stop_socket(soc):
    soc.close()


def main():
    open_socket()

if __name__ == "__main__":
    main()

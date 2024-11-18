
import threading
import json
import requests
import queue
import logging
import socket 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelName)s - %(message)s')
logger = logging.getLogger()

data_queue = queue.Queue()

CLOUD_URL = "http://localhost:3000"

# This function send json to cloud
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

    soc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server = '127.0.0.1'
    port = 3000
    soc.bind((server, port))
    soc.listen(1000)
    client_socket, client_address = soc.accept()
    data = client_socket.recv(1024)
    print(f": {data.decode()}")
    client_socket.sendall("".encode())
    client_socket.close()
    soc.close()




def main():



    thread_for_cloud = threading.Thread(target=send_data_to_cloud, daemon=True)
    collector_thread = threading.Thread(target=collect_data, daemon=True)

    thread_for_cloud.start()
    collector_thread.start()

    thread_for_cloud.join()
    collector_thread.join()


if __name__ == "__main__":
    main()




import socket
from src.app_gui.global_variables import global_variables_state
from src.models.processed_flight_data import ProcessedFlightData
import json
import logging

class SocketController:
    def __init__(self,route_id, platform_flight_index, platform_id,
                      platform_name, date,update_connection_status_message, 
                      show_error_in_screen,update_traffic_light_status, increment_received_json_counter): 
        
        self.logger: logging.Logger=global_variables_state["logger"].get_logger()
        self.connection_status_flag = global_variables_state["connection_status_flag"]
        self.config = global_variables_state["config"]

        self.route_id = route_id
        self.platform_flight_index = platform_flight_index
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.date = date

        self.update_connection_status_message = update_connection_status_message
        self.show_error_in_screen = show_error_in_screen
        self.update_traffic_light_status = update_traffic_light_status
        self.increment_received_json_counter = increment_received_json_counter
        self.create_server = False
        


        self.ProcessedFlightData = ProcessedFlightData(**self.collect_flight_data_to_dict())

        self.server_socket = None
        self.IP:str = self.config.get('settings', 'IP')
        self.PORT:int = self.config.getint('settings', 'PORT')
        self.SIZE_BYTES_FROM_DRONE:int = self.config.getint('settings', 'SIZE_BYTES_FROM_DRONE')

    def collect_flight_data_to_dict(self):
        return {
        'route_id': str(self.route_id.value),
        'platform_name': str( self.platform_name.value),
        'platform_id':int( self.platform_id.value),
        'date': str(self.date.text) ,
        'platform_flight_index': int(self.platform_flight_index.value),
        'show_error_in_screen': self.show_error_in_screen,
    }


    def create_server_socket(self):
        try:
            self.server_socket: socket.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            self.logger.error(f"Error creating server socket: {e}")
            self.show_error_in_screen("Error creating server socket")

    def listen_for_connection(self):
        SOCKET_LISTEN:int = self.config.getint('settings', 'SOCKET_LISTEN') or 1
        self.server_socket.listen(SOCKET_LISTEN)
        self.server_socket.settimeout(10)
        self.logger.info("Waiting for drone to connect")
    
    def accept_connection(self):
        try:
            self.logger.info("Waiting for drone to connect")
            server, address = self.server_socket.accept()
            self.logger.info(f"connection to drone")
            self.message_view("connection to drone")
            return server
        except socket.timeout:
            return False
        except Exception as e:
            self.show_error_in_screen("Error while waiting for drone connection")
            return False

    def receive_data(self, server):
        try:
            data: bytes = server.recv(self.SIZE_BYTES_FROM_DRONE)
            if not data:
                return None
            self.logger.info("Data received from drone")
            # self.increment_received_json_counter()
            return data
        except socket.timeout:
            return False
        except Exception as e:
            self.show_error_in_screen("Error receiving data from drone")
            return False
        
    def process_data(self, data):
        try:
            json_str:json = data.decode('utf-8')
            data:str=json.loads(json_str)
            self.ProcessedFlightData.process_flight_data(**data)
            
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            self.show_error_in_screen("Error processing data")


    def close_socket(self):
        if self.server_socket:
            try:
                self.server_socket.close()
                self.logger.info("Socket closed")
            except Exception as e:
                self.logger.error(f"Failed to close the socket: {e}")
                self.show_error_in_screen("Failed to close the socket")


    def bind_socket(self):
        
        try:
            self.server_socket.bind((self.IP, self.PORT))
            self.logger.info(f"Successfully bound to IP and port, the ip is:{self.IP} and port : {self.PORT}")
            return True
        except Exception as e:
            return



    def run(self):
        
        self.create_server_socket()
        
        while self.connection_status_flag.is_set():

            while not self.create_server and self.connection_status_flag.is_set():
                if self.bind_socket():
                    break
           
            self.listen_for_connection()
        
            while self.connection_status_flag.is_set():

                server = self.accept_connection()

                if not server:
                    continue
                elif server:
                    while self.connection_status_flag.is_set():
                        data = self.receive_data(server)
                        if data:
                            self.process_data(data)
                        else:
                            continue

        self.close_socket()



    
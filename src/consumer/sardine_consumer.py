import socket
import json
import logging
import datetime
import threading
import configparser
from queue import Queue
from typing import Dict
from json.decoder import JSONDecodeError

from src.GUI.global_variables import global_variables_state
from src.models.flight_data import FlightData


class SardineConsumer:
    def __init__(self,data_queue:Queue,is_sardine_connection_active_flag: threading.Event,**kwargs: Dict[str, any]): 
         
        for key, value in kwargs.items():
            setattr(self, key, value) 
        
        self.logger:logging.Logger=global_variables_state["logger"].get_logger()
        self.is_sardine_connection_active_flag: threading.Event= is_sardine_connection_active_flag
        self.config: configparser.ConfigParser = global_variables_state["config"]
        self.data_queue:Queue=data_queue

        self.server_socket = None
        self.IP:str = self.config.get('settings', 'IP')
        self.PORT:int = self.config.getint('settings', 'PORT')
        self.SIZE_BYTES_FROM_DRONE:int = self.config.getint('settings', 'SIZE_BYTES_FROM_DRONE')


    def create_server_socket(self)-> None:
        try:
            self.server_socket: socket.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logger.info(f"creating server socket")
        except Exception as e:
            self.logger.error(f"Error creating server socket: {e}")
            self.show_error_in_screen("Error creating server socket")


    def listen_for_connection(self)-> None:
        try:
            self.server_socket.settimeout(5)
            SOCKET_LISTEN:int = self.config.getint('settings', 'SOCKET_LISTEN') or 1
            self.server_socket.listen(SOCKET_LISTEN)
            self.logger.info(f"Server is listening for connections with a timeout of {SOCKET_LISTEN}")
        except Exception as e:
            self.logger.error(f"Error occurred while setting up the server socket: {e}")
            self.show_error_in_screen("Error occurred while setting up the server socket")

    
    def accept_connection(self):
        try:
            self.logger.info("Waiting for drone to connect")
            self.server, address = self.server_socket.accept()
            self.logger.info(f"connection to drone")
            self.update_connection_status_message("connection to drone")
        except socket.timeout:
            self.logger.warning("Timeout occurred while waiting for data from the drone.")
            return True
        except ConnectionResetError as e:
            self.logger.error(f"Connection reset error occurred: {str(e)}")
            return False
        except OverflowError as e:
            self.logger.error(f"Overflow error occurred: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error while waiting for drone connection: {str(e)}")
            self.show_error_in_screen("Error while waiting for drone connection")
            return False


    def receive_data(self, server):
        try:
            data: bytes = server.recv(self.SIZE_BYTES_FROM_DRONE)
            print(data)
            if not data:
                return False
            self.logger.info("Data received from drone")
            self.update_traffic_light_status("yellow")
            self.increment_received_json_counter()
            return data
        except socket.timeout:
            self.logger.warning("Timeout occurred while data received from drone.")
            return
        except socket.error as e:
            self.logger.error(f"Socket error occurred while receiving data: {str(e)}")
            return False
        except ConnectionResetError as e:
            self.logger.error(f"Connection reset error occurred while receiving data: {str(e)}")
            self.show_error_in_screen("Connection reset error occurred while receiving data")
            return False
        except Exception as e:
            self.show_error_in_screen(f"Error receiving data from drone: {e}")
            return False

   
    def process_data(self, data)-> None:
        try:
            json_str:str = data.decode('utf-8')
            data:dict =json.loads(json_str)
            all_flight_data:dict=self.process_flight_data(**data)
            print(all_flight_data)
            if all_flight_data:
                flight_data=FlightData(**all_flight_data)
            self.add_json_to_queue(flight_data)
        except JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format: {e}")
        except ValueError as e:
           self.logger.error(f"Validation error: {e}")  
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")


    def close_socket(self)-> None:
        if self.server_socket:
            try:
                self.server_socket.close()
                self.logger.info("Socket closed")
            except Exception as e:
                self.logger.error(f"Failed to close the socket: {e}")


    def bind_socket(self):
        try:
            self.logger.info(f"Waiting to bind IP and port, the ip is:{self.IP} and port : {self.PORT}")
            self.server_socket.bind((self.IP, self.PORT))
            self.logger.info(f"Successfully bound to IP and port, the ip is:{self.IP} and port : {self.PORT}")
            return True
        except socket.error as e:
            self.logger.error(f"Socket error occurred while binding to IP: {self.IP} and port: {self.PORT}. Error: {str(e)}")
            return False
        except PermissionError as e:
            self.logger.error(f"Permission error occurred while binding to IP: {self.IP} and port: {self.PORT}. Error: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Waiting bind to IP and port, the ip is:{self.IP} and port : {self.PORT}")
            return


    def process_flight_data(self, azimuth: float,coordinate: list,height: float,
                            timeOfLastKnownLocation: str,droneId: int) -> dict:
        print(1)
        try:
            flight_id:str = self._generate_flight_id(self.platform_name, self.platform_id, self.date, self.platform_flight_index)

            processed_data :dict = {
                "AZIMUTH": self.round_to_decimal_places(azimuth, 2),
                "COORDINATE": {
                    "latitude": self.round_to_decimal_places(coordinate[0], 7),
                    "longitude": self.round_to_decimal_places(coordinate[1], 7)
                },
                "DATE": self.date,
                "Platform_Flight_Index": int(self.platform_flight_index),
                "FLIGHT_ID": flight_id,
                "HEIGHT": self.round_to_decimal_places(height, 1),
                "PITCH": 0.0,
                "PLATFORMID": int(self.platform_id),
                "PLATFORMNAME": self.platform_name,
                "ROLL": 0.0,
                "ROUTEID": self.route_id,
                "TIMEOFLASTKNOWNLOCATION": timeOfLastKnownLocation
            }
            return processed_data

        except Exception as e:
            self.logger.error(f"Error processing flight data: {e}")
            self.show_error_in_screen(f"Error processing flight data: {e}")
            

    @staticmethod
    def round_to_decimal_places(number_to_float: float, decimal_places:int)->float:
        return round(number_to_float, decimal_places)


    def _generate_flight_id(self, platform_name, platform_id, date, platform_flight_index)-> str:
        conversion_date_for_flight_id:str = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
        return f"{platform_name}{platform_id}_{conversion_date_for_flight_id}_{str(platform_flight_index).zfill(4)}"


    def clear_queue(self)-> None:
        while not self.data_queue.empty():
            try:
                self.data_queue.get_nowait()
                self.logger.debug("Item successfully removed from queue.")
            except Exception as e:
                self.logger.error(f"Failed to clear the queue: {e}")
            

    def add_json_to_queue(self,data_to_queue: dict)->None:
        try:
            if self.data_queue.full():
                self.clear_queue() 
                self.logger.info("Queue has been cleared successfully.")
                            
            self.data_queue.put(data_to_queue)

            self.logger.info("Data added to queue")
        except Exception as e:
            self.logger.error(f"Failed to add data to queue: {e}")


    def initialize_socket(self):
        self.create_server_socket()
        self.bind_socket()
        self.listen_for_connection()



    def sardine_connection_active_flag(self):
        return  self.is_sardine_connection_active_flag.is_set()


    def run(self):

        while self.sardine_connection_active_flag():
            self.initialize_socket()
        
            while self.sardine_connection_active_flag():

                server_time_out = self.accept_connection()

                if server_time_out: continue
                if server_time_out==False: break

                
                while self.sardine_connection_active_flag():

                    data = self.receive_data(self.server)

                    if data : self.process_data(data)
                    if data==False : break

        self.close_socket()
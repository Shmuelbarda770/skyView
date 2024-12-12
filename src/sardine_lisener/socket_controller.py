
import socket
from src.app_gui.global_variables import global_variables_state


class SocketController:
    def __init__(self,route_id, platform_flight_index, platform_id,
                                          platform_name, date,status_indicator_unconnected,
                                          status_indicator_connected_and_receives_data, status_indicator_send_to_cloud,
                                          status_connection, received_json_counter,
                                          sent_json_counter, show_running_error,update_traffic_light_status,
                                          increment_received_json_counter ): 
        
        self.logger=global_variables_state["logger"].get_logger()
        self.connection_status_flag = global_variables_state["connection_status_flag"]
        self.config = global_variables_state["config"]

        self.route_id = route_id
        self.platform_flight_index = platform_flight_index
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.date = date
        self.status_indicator_unconnected = status_indicator_unconnected
        self.status_indicator_connected_and_receives_data = status_indicator_connected_and_receives_data
        self.status_indicator_send_to_cloud = status_indicator_send_to_cloud
        self.status_connection = status_connection
        self.received_json_counter = received_json_counter
        self.sent_json_counter = sent_json_counter
        self.show_running_error = show_running_error
        self.update_traffic_light_status=update_traffic_light_status
        self.increment_received_json_counter = increment_received_json_counter
        self.create_server = False


        self.server_socket = None
        self.IP = self.config.get('settings', 'IP')
        self.PORT = self.config.getint('settings', 'PORT')
        self.SIZE_BYTES_FROM_DRONE = self.config.getint('settings', 'SIZE_BYTES_FROM_DRONE')



    def create_server_socket(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            self.logger.error(f"Error creating server socket: {e}")
            self.show_running_error(self.running_problems, "Error creating server socket")

    def listen_for_connection(self):
        SOCKET_LISTEN = self.config.getint('settings', 'SOCKET_LISTEN') or 1
        self.server_socket.listen(SOCKET_LISTEN)
        self.server_socket.settimeout(10)
        self.logger.info("Waiting for drone to connect")
    
    def accept_connection(self):
        try:
            self.logger.info("Waiting for drone to connect")
            server, address = self.server_socket.accept()
            self.logger.info(f"connection to drone")
            # message_view(self.status_connection, "connection to drone")
            return server
        except socket.timeout:
            return False
        except Exception as e:
            self.show_running_error("Error while waiting for drone connection")
            return False

    def receive_data(self, server):
        try:
            data = server.recv(self.SIZE_BYTES_FROM_DRONE)
            if not data:
                return None
            self.logger.info("Data received from drone")
            return data
        except socket.timeout:
            return False
        except Exception as e:
            self.show_running_error("Error receiving data from drone")
            return False
        
    def process_data(self, data):
        try:
            return
        #     processed_data = upData_json(data, self.route_id, self.platform_name, self.platform_id,
        #                                  self.date, self.platform_flight_index, self.running_problems)
        #     if processed_data:
                # queue_status(processed_data)
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            self.show_running_error("Error processing data")


    def close_socket(self):
        if self.server_socket:
            try:
                self.server_socket.close()
                self.logger.info("Socket closed")
            except Exception as e:
                self.logger.error(f"Failed to close the socket: {e}")
                self.show_running_error("Failed to close the socket")


    import socket

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



    
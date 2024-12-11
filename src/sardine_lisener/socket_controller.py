
from updatePage import show_error_in_screen,message_view
import socket
from app_gui.global_variables import global_variables_state

class SocketController:
    def __init__(self, route_id, platform_flight_index, platform_id, platform_name, date,
                 status_indicator_red, status_indicator_yellow, status_indicator_green, status_connection,
                 cont_json_received, cont_send_json_to_cloud, running_problems):
        
        self.logger=global_variables_state["logger"]
        self.connection_status_flag =  global_variables_state["connection_status_flag"]
        self.route_id = route_id
        self.platform_flight_index = platform_flight_index
        self.platform_id = platform_id
        self.platform_name = platform_name
        self.date = date
        self.status_indicator_red = status_indicator_red
        self.status_indicator_yellow = status_indicator_yellow
        self.status_indicator_green = status_indicator_green
        self.status_connection = status_connection
        self.cont_json_received = cont_json_received
        self.cont_send_json_to_cloud = cont_send_json_to_cloud
        self.running_problems = running_problems
        self.logger=global_variables_state["logger"]


        self.server_socket = None
        self.IP = config.get('settings', 'IP')
        self.PORT = config.getint('settings', 'PORT')
        self.SIZE_BYTES_FROM_DRONE = config.getint('settings', 'SIZE_BYTES_FROM_DRONE')



    def create_server_socket(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            self.logger.error(f"Error creating server socket: {e}")
            show_error_in_screen(self.running_problems, "Error creating server socket")

    def listen_for_connection(self):
        SOCKET_LISTEN = config.getint('settings', 'SOCKET_LISTEN') or 1
        self.server_socket.listen(SOCKET_LISTEN)
        self.server_socket.settimeout(10)
        self.logger.info("Waiting for drone to connect")
    
    def accept_connection(self):
        try:
            server, address = self.server_socket.accept()
            self.logger.info(f"connection to drone")
            message_view(self.status_connection, "connection to drone")
            return server
        except socket.timeout:
            return None
        except Exception as e:
            self.logger.error(f"Error while waiting for drone connection: {e}")
            show_error_in_screen(self.running_problems, "Error while waiting for drone connection")
            return None

    def receive_data(self, server):
        try:
            data = server.recv(self.SIZE_BYTES_FROM_DRONE)
            if not data:
                return None
            self.logger.info("Data received from drone")
            return data
        except socket.timeout:
            return None
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            show_error_in_screen(self.running_problems, "Error receiving data from drone")
            return None
        
    def process_data(self, data):
        try:
            processed_data = upData_json(data, self.route_id, self.platform_name, self.platform_id,
                                         self.date, self.platform_flight_index, self.running_problems)
            if processed_data:
                queue_status(processed_data)
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            show_error_in_screen(self.running_problems, "Error processing data")

    def close_socket(self):
        if self.server_socket:
            try:
                self.server_socket.close()
                self.logger.info("Socket closed")
            except Exception as e:
                self.logger.error(f"Failed to close the socket: {e}")
                show_error_in_screen(self.running_problems, "Failed to close the socket")

    def run(self):
        while self.connection_status_flag.is_set():
            if self.create_server_socket():
                break

        while self.connection_status_flag.is_set():
            if self.bind_socket():
                break
        
        self.listen_for_connection()

        while self.connection_status_flag.is_set():
            server = self.accept_connection()
            if server:
                while self.connection_status_flag.is_set():
                    data = self.receive_data(server)
                    if data:
                        self.process_data(data)
                    else:
                        break

        self.close_socket()



    
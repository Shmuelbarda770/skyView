import socket
import threading

def receive_messages(client_socket):
    """Function to listen for messages from the server"""
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"Server says: {message.decode()}")
        except Exception as e:
            print(f"Error receiving messages: {e}")
            break


def send_messages(client_socket):
    """Function to send messages to the server"""
    while True:
        message = input("What do you want to send to the server? ")
        client_socket.send(message.encode())


def start_client():
    """Function to connect to the server"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 65432)  # Server's IP address and port
    client_socket.connect(server_address)

    print("Connected to the server!")

    # Create threads for listening and sending messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()


if __name__ == "__main__":
    start_client()

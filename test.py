import socket
import time

def send_data_to_client():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p = '127.0.0.1' 
    port = 3000  
    
    try:
        soc.connect((p, port))  
        print("Connected to the client successfully.")
        
        while True:
            message = "New data" 
            soc.send(message.encode()) 
            print(f"Sent data: {message}")
            time.sleep(2) 
    
    except Exception as e:
        print(f"Error connecting to the client: {e}")
    
    finally:
        soc.close() 

def main():
    send_data_to_client()

if __name__ == "__main__":
    main()

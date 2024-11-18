import socket
import time

def send_data():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = '127.0.0.1' 
    port = 3000  
    
    try:
        soc.connect((ip, port))  
        print("Connected to the client successfully.")
        
        while True:
            message = "New data" 
            soc.send(message.encode()) 
            print(f"Sent data: {message}")
            time.sleep(2) 
    
    except Exception as e:
        print(f"Error type: {e}")
    
    finally:
        soc.close() 

def main():
    send_data()

if __name__ == "__main__":
    main()

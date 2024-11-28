import socket
import time
import json

def send_data():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = '127.0.0.1' 
    port = 3000 
    
    try:
        soc.connect((ip, port))  
        print("Connected to the client successfully.")
        
        while True:
           
            data ={'azimuth': 309.92948031140907, 
                   'height': 265,
                   'roll':100.4,
                   'pitch':100.5,
                    'drone_id': 2,
                    'timeOfLastKnownLocation':"1999-01-01T23:59:59Z",
                    'coordinate': [32.97796960706076,35.57318255832567]}
           
            print(len(data['coordinate']))
            json_data = json.dumps(data)
           
            json_data=json_data.encode() 
            print(json_data)
            soc.send(json_data)
            print(f"Sent data: {json_data}")
            time.sleep(1)
    
    except Exception as e:
        print(f"Error type: {e}")
    
    finally:
        soc.close()

def main():
    send_data()

if __name__ == "__main__":
    main()

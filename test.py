import socket
import time
import json  
import numpy as np
import pickle
def send_data():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = '127.0.0.1' 
    port = 3000 
    
    try:
        soc.connect((ip, port))  
        print("Connected to the client successfully.")
        
        while True:
           
            data ={'azimuth': np.float64(309.92948031140907), 
                   'height': 265.9026023199988,
                   'roll':6554,
                   'pitch':654,
                    'drone_id': 2,
                    'timeOfLastKnownLocation': 1732101436.9894395,
                    'coordinate': [np.float64(32.97796960706076), np.float64(35.57318255832567)]}
            print(type(data))
            json_data = json.dumps(data)
            print(json_data)
            print(data)
            print(type(json_data))
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

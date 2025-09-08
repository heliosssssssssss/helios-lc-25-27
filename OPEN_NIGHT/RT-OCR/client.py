import socket
import time
from console import console

class LogTransmitter:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            console.notify("LogTransmitter", f"Connected to receiver at {self.host}:{self.port}")
            return True
        except Exception as e:
            console.alert("LogTransmitter", f"Failed to connect: {e}")
            return False
    
    def send_log(self, message):
        if self.connected and self.socket:
            try:
                self.socket.send(message.encode('utf-8'))
            except Exception as e:
                console.alert("LogTransmitter", f"Send error: {e}")
                self.connected = False
    
    def disconnect(self):
        self.connected = False
        if self.socket:
            self.socket.close()
        console.log("LogTransmitter", "Disconnected from receiver")

def main():
    transmitter = LogTransmitter()
    
    if not transmitter.connect():
        return
    
    try:
        console.log("LogTransmitter", "Starting log transmission...")
        
        while True:
            test_message = f"[TEST] {time.strftime('%H:%M:%S')} - Test log message\n"
            transmitter.send_log(test_message)
            time.sleep(2)
            
    except KeyboardInterrupt:
        console.warn("LogTransmitter", "Stopping transmission...")
    finally:
        transmitter.disconnect()

if __name__ == "__main__":
    main()

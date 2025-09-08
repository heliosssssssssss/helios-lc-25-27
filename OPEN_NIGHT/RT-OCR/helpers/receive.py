import socket
import threading
import time
from console import console

class Receiver:
    def __init__(self):
        self.host = "192.168.1.100"
        self.port = 9999
        self.client_socket = None
        self.running = False
        
    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.running = True
            
            console.set_mode("CLIENT")
            console.log("Receiver", f"Connected to {self.host}:{self.port}")
            console.set_receive_socket(self.client_socket)
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            console.alert("Receiver", f"Connection error: {e}")
        finally:
            self.cleanup()
            
    def receive_messages(self):
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                console.log("Receiver", f"Received: {message}")
                
        except Exception as e:
            console.warn("Receiver", f"Receive error: {e}")
            
    def cleanup(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        console.log("Receiver", "Connection closed")

if __name__ == "__main__":
    receiver = Receiver()
    try:
        receiver.connect_to_server()
    except KeyboardInterrupt:
        console.warn("Receiver", "Interrupted by user")
    except Exception as e:
        console.alert("Receiver", f"Fatal error: {e}")

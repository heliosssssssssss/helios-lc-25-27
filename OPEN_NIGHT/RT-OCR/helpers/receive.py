import socket
import threading
import time
import os
from console import console

class Receiver:
    def __init__(self):
        self.host = "192.168.56.1"
        self.port = 9999
        self.client_socket = None
        self.running = False
        
    def connect_to_server(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=" * 60)
            print("           RT-OCR RECEIVER WINDOW")
            print("=" * 60)
            print()
            print(f"Attempting to connect to: {self.host}:{self.port}")
            print("=" * 60)
            print()
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(10)
            self.client_socket.connect((self.host, self.port))
            self.running = True
            
            console.set_mode("CLIENT")
            console.log("Receiver", f"Connected to {self.host}:{self.port}")
            console.set_receive_socket(self.client_socket)
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            print("Connected successfully! Press Ctrl+C to exit.")
            print("=" * 60)
            print()
            
            while self.running:
                time.sleep(1)
                
        except socket.timeout:
            console.alert("Receiver", f"Connection timeout to {self.host}:{self.port}")
            input("Press Enter to exit...")
        except ConnectionRefusedError:
            console.alert("Receiver", f"Connection refused to {self.host}:{self.port}")
            console.warn("Receiver", "Make sure transmitter is running first")
            input("Press Enter to exit...")
        except Exception as e:
            console.alert("Receiver", f"Connection error: {e}")
            input("Press Enter to exit...")
        finally:
            self.cleanup()
            
    def receive_messages(self):
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    console.warn("Receiver", "Server disconnected")
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
        input("Press Enter to exit...")

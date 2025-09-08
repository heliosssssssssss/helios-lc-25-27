import socket
import threading
import time
import os
from console import console

class Transmitter:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 9999
        self.server_socket = None
        self.clients = []
        self.running = False
        
    def start_server(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=" * 60)
            print("           RT-OCR TRANSMITTER WINDOW")
            print("=" * 60)
            print()
            
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            console.set_mode("HOST")
            console.log("Transmitter", f"Server started on {self.host}:{self.port}")
            console.notify("Transmitter", "Waiting for connections...")
            
            actual_ip = socket.gethostbyname(socket.gethostname())
            print(f"Server binding to: {self.host} (all interfaces)")
            print(f"Actual machine IP: {actual_ip}")
            print(f"Port: {self.port}")
            print("=" * 60)
            print()
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.clients.append(client_socket)
                    console.notify("Transmitter", f"Client connected: {client_address[0]}:{client_address[1]}")
                    console.set_client_socket(client_socket)
                    
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    break
                    
        except Exception as e:
            console.alert("Transmitter", f"Server error: {e}")
        finally:
            self.cleanup()
            
    def handle_client(self, client_socket, client_address):
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                console.log("Transmitter", f"Received from {client_address[0]}: {message}")
                
        except Exception as e:
            console.warn("Transmitter", f"Client {client_address[0]} disconnected: {e}")
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
            
    def cleanup(self):
        self.running = False
        for client in self.clients:
            client.close()
        if self.server_socket:
            self.server_socket.close()
        console.log("Transmitter", "Server shutdown complete")

if __name__ == "__main__":
    transmitter = Transmitter()
    try:
        transmitter.start_server()
    except KeyboardInterrupt:
        console.warn("Transmitter", "Interrupted by user")
    except Exception as e:
        console.alert("Transmitter", f"Fatal error: {e}")

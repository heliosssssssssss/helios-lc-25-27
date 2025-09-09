import socket
import threading
import sys
from outbound import Outbound

class LogServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.clients = []
        self.running = False
        self.server_socket = None
        self.logger = Outbound(True, True)
        
    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.logger.success("SERVER", f"Started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.logger.log("SERVER", f"Client connected from {client_address}")
                    
                    self.clients.append(client_socket)
                    
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        self.logger.error("SERVER", f"Connection error: {e}")
                        
        except Exception as e:
            self.logger.error("SERVER", f"Server error: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        try:
            while self.running:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    message = data.decode('utf-8').strip()
                    self.broadcast(message)
                    
                except socket.error:
                    break
                    
        except Exception as e:
            self.logger.error("SERVER", f"Client error {client_address}: {e}")
        finally:
            self.remove_client(client_socket)
            client_socket.close()
            self.logger.warn("SERVER", f"Client {client_address} disconnected")
    
    def broadcast(self, message):
        if not self.clients:
            return
            
        disconnected_clients = []
        
        for client in self.clients:
            try:
                client.send(f"{message}\n".encode('utf-8'))
            except socket.error:
                disconnected_clients.append(client)
        
        for client in disconnected_clients:
            self.remove_client(client)
    
    def remove_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)
    
    def stop(self):
        self.running = False
        
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.logger.warn("SERVER", "Server stopped")

if __name__ == "__main__":
    server = LogServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

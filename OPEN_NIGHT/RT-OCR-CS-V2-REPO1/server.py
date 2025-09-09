

import socket
import threading
import time
from datetime import datetime

class ConsoleStreamServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.clients = []
        self.running = False
        self.server_socket = None
        
    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            print(f"Server started on {self.host}:{self.port}")
            print("Waiting for client connections...")
            print("Type 'quit' to stop the server")
            
            input_thread = threading.Thread(target=self.monitor_console_input, daemon=True)
            input_thread.start()
            
            status_thread = threading.Thread(target=self.send_status_updates, daemon=True)
            status_thread.start()
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"Client connected from {client_address}")
                    
                    self.clients.append(client_socket)
                    
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop_server()
    
    def handle_client(self, client_socket, client_address):
        try:
            # sws_1
            welcome_msg = f"Connected to console stream server at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            client_socket.send(welcome_msg.encode('utf-8'))
            
            while self.running:
                try:
                    client_socket.send(b"PING\n")
                    time.sleep(30) 
                except socket.error:
                    break
                    
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            self.remove_client(client_socket)
            client_socket.close()
            print(f"Client {client_address} disconnected")
    
    def monitor_console_input(self):
        while self.running:
            try:
                user_input = input()
                
                if user_input.lower() == 'quit':
                    print("Shutting down server...")
                    self.running = False
                    break
                
                timestamp = datetime.now().strftime('%H:%M:%S')
                message = f"[{timestamp}] Console: {user_input}\n"
                self.broadcast_message(message)
                
            except EOFError:
                break
            except Exception as e:
                print(f"Error reading console input: {e}")
    
    def send_status_updates(self):
        while self.running:
            try:
                time.sleep(60)
                if self.clients:
                    status_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Server Status: {len(self.clients)} client(s) connected\n"
                    self.broadcast_message(status_msg)
            except Exception as e:
                print(f"Error sending status update: {e}")
    
    def broadcast_message(self, message):
        if not self.clients:
            return
            
        disconnected_clients = []
        
        for client in self.clients:
            try:
                client.send(message.encode('utf-8'))
            except socket.error:
                disconnected_clients.append(client)
        
        for client in disconnected_clients:
            self.remove_client(client)
    
    def remove_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)
    
    def stop_server(self):
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
        
        print("Server stopped")

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"
    
    print(f"Local IP address: {local_ip}")
    print("Starting Console Stream Server...")
    
    server = ConsoleStreamServer(host='0.0.0.0', port=8888)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
        server.stop_server()

if __name__ == "__main__":
    main()

import socket
import threading
from console import console

class LogReceiver:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            
            console.notify("LogReceiver", f"Server listening on {self.host}:{self.port}")
            console.log("LogReceiver", "Waiting for transmitter connection...")
            
            self.running = True
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    console.notify("LogReceiver", f"Connected to transmitter: {client_address}")
                    
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        console.alert("LogReceiver", "Error accepting connection")
                    break
                    
        except Exception as e:
            console.alert("LogReceiver", f"Server error: {e}")
        finally:
            self.stop_server()
    
    def handle_client(self, client_socket, client_address):
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8')
                if message.strip():
                    print(message)  # Print received log directly
                    
        except Exception as e:
            console.alert("LogReceiver", f"Client handling error: {e}")
        finally:
            client_socket.close()
            console.warn("LogReceiver", f"Disconnected from {client_address}")
    
    def stop_server(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        console.log("LogReceiver", "Server stopped")

def main():
    receiver = LogReceiver()
    try:
        receiver.start_server()
    except KeyboardInterrupt:
        console.warn("Main", "Shutting down server...")
        receiver.stop_server()

if __name__ == "__main__":
    main()

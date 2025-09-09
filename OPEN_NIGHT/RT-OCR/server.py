import socket
import threading
from outbound import Outbound

class LogServer:
    def __init__(self, port=8888):
        self.port = port
        self.clients = []
        self.out = Outbound(True, True)
        
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.listen(5)
        
        local_ip = self.get_local_ip()
        self.out.success("SERVER", f"Started on {local_ip}:{self.port}")
        self.out.log("SERVER", f"Connect with: python client.py --host {local_ip}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            self.out.log("SERVER", f"Client connected from {client_address}")
            
            self.clients.append(client_socket)
            
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
    
    def handle_client(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8').strip()
            self.broadcast(message)
        
        self.clients.remove(client_socket)
        client_socket.close()
        self.out.warn("SERVER", "Client disconnected")
    
    def broadcast(self, message):
        for client in self.clients[:]:
            try:
                client.send(f"{message}\n".encode('utf-8'))
            except:
                self.clients.remove(client)

if __name__ == "__main__":
    LogServer().start()

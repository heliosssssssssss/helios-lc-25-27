import socket
import threading
from outbound import Outbound

## HEY ! HEY ! [THIS IS A HELIOS INTERNATIONAL PROJECT | OPEN NIGHT 2025]

## [+] This project is outlined under no liscence, however falls under the h1k.org private Github, view h1k.org/git-redis/en for further)

# RECEIVE OUTBOUND TO CLIENT(S)

class LogServer:
    def __init__(self, port=8888):
        self.port = port
        self.clients = []
        self.out = Outbound(True, True)
        
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) # UDP -/ LOCAL
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.listen(5)
        
        local_ip = self.get_local_ip()
        self.out.success("SERVER", f"local -> {local_ip}:{self.port}")
        while True:
            client_socket, client_address = server_socket.accept()
            self.out.log("SERVER", f"inbound client ->{client_address}") # client connection to main
            
            self.clients.append(client_socket)
            # threadcontrol 1
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
    
    def handle_client(self, client_socket):
        try:
            while True: # HANDLE DISCONMNECT IN IF NOT
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8').strip()
                self.broadcast(message)
        except:
            pass
        finally:
            self.clients.remove(client_socket)
            client_socket.close()
            self.out.warn("SERVER", "Client disconnected")
    
    def broadcast(self, message): #replication
        for client in self.clients[:]:
            try:
                client.send(f"{message}\n".encode('utf-8'))
            except:
                self.clients.remove(client)

if __name__ == "__main__":
    LogServer().start()

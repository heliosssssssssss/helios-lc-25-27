import socket
import argparse
import os
from rich import print
from outbound import Outbound

class LogClient:
    def __init__(self, host, port=8888):
        self.host = host
        self.port = port
        self.out = Outbound(True, False)
        
    def start(self):
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_obj.connect((self.host, self.port))

        os.system(f"cls")
        
        self.out.success("CLIENT", f"Connected to {self.host}:{self.port}")
        
        while True:
            data = socket_obj.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8').strip()
            print(message)
        
        self.out.warn("CLIENT", "Disconnected")

parser = argparse.ArgumentParser()
parser.add_argument('--host', required=True, help='Server host')
parser.add_argument('--port', type=int, default=8888, help='Server port')
    
args = parser.parse_args()
LogClient(args.host, args.port).start()
import socket
import argparse
import os
from rich import print
from outbound import Outbound

## HEY ! HEY ! [THIS IS A HELIOS INTERNATIONAL PROJECT | OPEN NIGHT 2025]

# RECEIVE SERVER , TO PROCESS

class LogClient:
    def __init__(self, host, port=8888):
        self.host = host
        self.port = port
        self.out = Outbound(True, False)
        
    def start(self):
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_obj.connect((self.host, self.port))

        os.system(f"cls")
        
        self.out.success("CLIENT", f"successfully connected = {self.host}:{self.port}")
        
        while True: # stream
            data = socket_obj.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8').strip() # display msg
            message = message.replace('[/bold orange3]', '[/bold orange1]')
            message = message.replace('[bold orange3]', '[bold orange1]')
            try:
                print(message)
            except Exception as e: #BOLD ORANGE ^ 
                plain_message = message.replace('[bold yellow]', '').replace('[/bold yellow]', '') # fall back 2 
                plain_message = plain_message.replace('[bold cyan]', '').replace('[/bold cyan]', '') # fall back 2 
                plain_message = plain_message.replace('[bold white]', '').replace('[/bold white]', '')
                plain_message = plain_message.replace('[bold orange1]', '').replace('[/bold orange1]', '')
                plain_message = plain_message.replace('[bold red]', '').replace('[/bold red]', '')
                plain_message = plain_message.replace('[bold green]', '').replace('[/bold green]', '')
                print(plain_message)

parser = argparse.ArgumentParser()
parser.add_argument('--host', required=True, help='the ip')
parser.add_argument('--port', type=int, default=8888, help='the port')

args = parser.parse_args()
LogClient(args.host, args.port).start()
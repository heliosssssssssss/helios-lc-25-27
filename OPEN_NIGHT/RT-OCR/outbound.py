from rich import print
import socket
import datetime
import time

class Outbound:

    def __init__(self, is_debug : bool, is_server : bool):
        self.is_debug = is_debug
        self.is_server = is_server
        self.server_socket = None
        
        if self.is_server:
            self.connect_to_server()
    
    def connect_to_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect(('localhost', 8888))
        except:
            self.server_socket = None

    def get_timestamp(self):
        raw_timestamp = time.time()
        timestamp = datetime.datetime.fromtimestamp(raw_timestamp).strftime('[%H:%M:%S]')
        return timestamp

    def send_to_server(self, message):
        if self.server_socket:
            try:
                #fix #16
                import re
                plain_message = re.sub(r'\[/?[^\]]*\]', '', message)
                self.server_socket.send(f"{plain_message}\n".encode('utf-8'))
            except:
                pass

    def log(self, state : str, context : str, speaker = None): # white
        message = f"[bold yellow]{self.get_timestamp()}[/bold yellow] @ [bold cyan]{state}[/bold cyan] : [bold white](LOG)[/bold white] -> {context}"
        print(message)
        if self.is_server:
            self.send_to_server(message)

    def warn(self, state : str, context : str, speaker = None): # orange
        message = f"[bold yellow]{self.get_timestamp()}[/bold yellow] @ [bold cyan]{state}[/bold cyan] : [bold orange3](WARN)[/bold orange3] -> {context}"
        print(message)
        if self.is_server:
            self.send_to_server(message)

    def info(self, state : str, context : str, speaker = None): # white (copy fork of log)
        message = f"[bold yellow]{self.get_timestamp()}[/bold yellow] @ [bold cyan]{state}[/bold cyan] : [bold orange3](INFO-LOG)[/bold orange3] -> {context}"
        print(message)
        if self.is_server:
            self.send_to_server(message)

    def error(self, state : str, context : str, speaker = None): # red
        message = f"[bold yellow]{self.get_timestamp()}[/bold yellow] @ [bold cyan]{state}[/bold cyan] : [bold red](ERROR)[/bold red] -> {context}"
        print(message)
        if self.is_server:
            self.send_to_server(message)

    def success(self, state : str,  context : str, speaker = None): # green
        message = f"[bold yellow]{self.get_timestamp()}[/bold yellow] @ [bold cyan]{state}[/bold cyan] : [bold green](SUCCESS)[/bold green] -> {context}"
        print(message)
        if self.is_server:
            self.send_to_server(message)
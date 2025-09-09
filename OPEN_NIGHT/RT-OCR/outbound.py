from rich import print
import socket
import datetime
import time

## made in 09/09/25 -> COMP SCI CLASS MR ALLEN, @ HELIOS FR 
## HEY ! HEY ! [THIS IS A HELIOS INTERNATIONAL PROJECT | OPEN NIGHT 2025]

# TO SERVER 

class Outbound:

    def __init__(self, is_debug : bool, is_server : bool):
        self.is_debug = is_debug
        self.is_server = is_server
        self.server_socket = None # only for is_server true instance
        
        if self.is_server:
            self.connect_to_server()
    
    def connect_to_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect(('localhost', 8888)) # debug mode 
        except:
            self.server_socket = None

    def get_timestamp(self):  # [HH:MM:SS expected str]
        raw_timestamp = time.time()
        timestamp = datetime.datetime.fromtimestamp(raw_timestamp).strftime('[%H:%M:%S]')
        return timestamp

    def send_to_server(self, message):
        if self.server_socket:
            try:
                self.server_socket.send(f"{message}\n".encode('utf-8'))
            except: # fallback fix 1 for error on formatting
                pass

    def log(self, state : str, context : str, speaker = None): # white
        message = f"[bold yellow]{self.get_timestamp()}[/bold yellow] @ [bold cyan]{state}[/bold cyan] : [bold white](LOG)[/bold white] -> {context}"
        print(message)
        if self.is_server:
            self.send_to_server(message)

    def warn(self, state : str, context : str, speaker = None): # orange
        message = f"[bold yellow]{self.get_timestamp()}[/bold yellow] @ [bold cyan]{state}[/bold cyan] : [bold orange1](WARN)[/bold orange1] -> {context}"
        print(message)
        if self.is_server:
            self.send_to_server(message)

    def info(self, state : str, context : str, speaker = None): # white (copy fork of log)
        message = f"[bold yellow]{self.get_timestamp()}[/bold yellow] @ [bold cyan]{state}[/bold cyan] : [bold orange1](INFO-LOG)[/bold orange1] -> {context}"
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
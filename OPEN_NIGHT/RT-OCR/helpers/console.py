from rich.console import Console
from rich.text import Text
from datetime import datetime
import socket
import threading

class ConsoleLogger:
    def __init__(self):
        self.console = Console()
        self.hostname = socket.gethostname()
        self.mode = "HOST"
        self.transmit_socket = None
        self.receive_socket = None
        self.server_socket = None
        self.client_socket = None
        self.is_server = False
        
    def set_mode(self, mode):
        self.mode = mode
        
    def set_transmit_socket(self, socket):
        self.transmit_socket = socket
        
    def set_receive_socket(self, socket):
        self.receive_socket = socket
        
    def set_server_socket(self, socket):
        self.server_socket = socket
        self.is_server = True
        
    def set_client_socket(self, socket):
        self.client_socket = socket
        self.is_server = False
        
    def _format_message(self, class_name, message, color_style):
        timestamp = datetime.now().strftime("%H:%M:%S")
        mode_text = Text(f"[{self.mode}]", style="green")
        header_text = Text(f"[{timestamp} / {class_name}]", style=color_style)
        message_text = Text(f" : {message}", style=color_style)
        return mode_text + header_text + message_text
    
    def _send_to_transmitter(self, formatted_text):
        if self.transmit_socket:
            try:
                self.transmit_socket.send(formatted_text.encode('utf-8'))
            except:
                pass
                
    def _send_to_server(self, formatted_text):
        if self.server_socket:
            try:
                self.server_socket.send(formatted_text.encode('utf-8'))
            except:
                pass
                
    def _send_to_client(self, formatted_text):
        if self.client_socket:
            try:
                self.client_socket.send(formatted_text.encode('utf-8'))
            except:
                pass
    
    def log(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "white")
        self.console.print(formatted_text)
        self._send_to_transmitter(str(formatted_text))
        self._send_to_server(str(formatted_text))
        self._send_to_client(str(formatted_text))
    
    def warn(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "orange3")
        self.console.print(formatted_text)
        self._send_to_transmitter(str(formatted_text))
        self._send_to_server(str(formatted_text))
        self._send_to_client(str(formatted_text))
    
    def alert(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "red")
        self.console.print(formatted_text)
        self._send_to_transmitter(str(formatted_text))
        self._send_to_server(str(formatted_text))
        self._send_to_client(str(formatted_text))
    
    def notify(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "cyan")
        self.console.print(formatted_text)
        self._send_to_transmitter(str(formatted_text))
        self._send_to_server(str(formatted_text))
        self._send_to_client(str(formatted_text))

console = ConsoleLogger()

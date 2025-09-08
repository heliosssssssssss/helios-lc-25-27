from rich.console import Console
from rich.text import Text
from datetime import datetime
import socket

class ConsoleLogger:
    def __init__(self, enable_network=False, network_host='localhost', network_port=12345):
        self.console = Console()
        self.hostname = socket.gethostname()
        self.enable_network = enable_network
        self.network_host = network_host
        self.network_port = network_port
        self.network_socket = None
        
        if self.enable_network:
            self._setup_network()
    
    def _setup_network(self):
        try:
            self.network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.network_socket.connect((self.network_host, self.network_port))
        except Exception as e:
            self.enable_network = False
    
    def _format_message(self, class_name, message, color_style):
        timestamp = datetime.now().strftime("%H:%M:%S")
        host_text = Text("[HOST]", style="green")
        header_text = Text(f"[{timestamp} / {class_name}]", style=color_style)
        message_text = Text(f" : {message}", style=color_style)
        return host_text + header_text + message_text
    
    def _format_network_message(self, class_name, message, log_type):
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[HOST][{timestamp} / {class_name}] : {message}\n"
    
    def _send_network(self, class_name, message, log_type):
        if self.enable_network and self.network_socket:
            try:
                network_msg = self._format_network_message(class_name, message, log_type)
                self.network_socket.send(network_msg.encode('utf-8'))
            except Exception:
                self.enable_network = False
    
    def log(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "white")
        self.console.print(formatted_text)
        self._send_network(class_name, message, "log")
    
    def warn(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "orange3")
        self.console.print(formatted_text)
        self._send_network(class_name, message, "warn")
    
    def alert(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "red")
        self.console.print(formatted_text)
        self._send_network(class_name, message, "alert")
    
    def notify(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "cyan")
        self.console.print(formatted_text)
        self._send_network(class_name, message, "notify")

console = ConsoleLogger()

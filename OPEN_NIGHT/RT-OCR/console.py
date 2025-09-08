from rich.console import Console
from rich.text import Text
from datetime import datetime
import socket
import threading

class ConsoleLogger:
    def __init__(self, network_host=None, network_port=8888):
        self.console = Console()
        self.hostname = socket.gethostname()
        self.network_host = network_host
        self.network_port = network_port
        self.network_socket = None
        self.network_enabled = network_host is not None
        
        if self.network_enabled:
            self._setup_network()
    
    def _setup_network(self):
        try:
            self.network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.network_socket.bind(('0.0.0.0', self.network_port))
            self.network_socket.listen(1)
            self.console.print(f"[green]Network logging enabled on port {self.network_port}[/green]")
        except Exception as e:
            self.console.print(f"[red]Failed to setup network logging: {e}[/red]")
            self.network_enabled = False
    
    def _send_network_message(self, log_type, class_name, message):
        if not self.network_enabled or not self.network_socket:
            return
            
        try:
            network_message = f"{log_type}|{class_name}|{message}"
            # For now, we'll just store the message for when a client connects
            # In a real implementation, you'd maintain a list of connected clients
            pass
        except Exception as e:
            pass
    
    def _format_message(self, class_name, message, color_style):
        timestamp = datetime.now().strftime("%H:%M:%S")
        host_text = Text("[HOST]", style="green")
        header_text = Text(f"[{timestamp} / {class_name}]", style=color_style)
        message_text = Text(f" : {message}", style=color_style)
        return host_text + header_text + message_text
    
    def log(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "white")
        self.console.print(formatted_text)
        self._send_network_message("LOG", class_name, message)
    
    def warn(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "orange3")
        self.console.print(formatted_text)
        self._send_network_message("WARN", class_name, message)
    
    def alert(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "red")
        self.console.print(formatted_text)
        self._send_network_message("ALERT", class_name, message)
    
    def notify(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "cyan")
        self.console.print(formatted_text)
        self._send_network_message("NOTIFY", class_name, message)

console = ConsoleLogger(network_host='0.0.0.0', network_port=8888)

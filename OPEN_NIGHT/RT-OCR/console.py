from rich.console import Console
from rich.text import Text
from datetime import datetime
import socket

class ConsoleLogger:
    def __init__(self):
        self.console = Console()
        self.hostname = socket.gethostname()
    
    def _format_message(self, class_name, message, color_style):
        timestamp = datetime.now().strftime("%H:%M:%S")
        host_text = Text("[HOST]", style="green")
        header_text = Text(f"[{timestamp} / {class_name}]", style=color_style)
        message_text = Text(f" : {message}", style=color_style)
        return host_text + header_text + message_text
    
    def log(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "white")
        self.console.print(formatted_text)
    
    def warn(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "orange3")
        self.console.print(formatted_text)
    
    def alert(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "red")
        self.console.print(formatted_text)
    
    def notify(self, class_name, message):
        formatted_text = self._format_message(class_name, message, "cyan")
        self.console.print(formatted_text)

console = ConsoleLogger()

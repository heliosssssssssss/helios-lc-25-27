import socket
import threading
import sys
import argparse
from rich.console import Console
from rich.text import Text

class NetworkReceiver:
    def __init__(self, host, port=8888):
        self.host = host
        self.port = port
        self.console = Console()
        self.running = False
        self.socket = None
        
    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            
            self.console.print(f"[green]Connected to {self.host}:{self.port}[/green]")
            self.console.print("[yellow]Receiving console messages... Press Ctrl+C to quit[/yellow]")
            
            while self.running:
                try:
                    data = self.socket.recv(1024)
                    if not data:
                        break
                    
                    message = data.decode('utf-8')
                    self.display_message(message)
                    
                except socket.error as e:
                    self.console.print(f"[red]Socket error: {e}[/red]")
                    break
                    
        except ConnectionRefusedError:
            self.console.print(f"[red]Connection refused to {self.host}:{self.port}[/red]")
            self.console.print("[yellow]Make sure the sender is running and listening on this address[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
        finally:
            self.cleanup()
    
    def display_message(self, message):
        try:
            parts = message.split('|', 2)
            if len(parts) == 3:
                log_type, class_name, msg = parts
                
                if log_type == "LOG":
                    self.console.print(f"[white][{class_name}] : {msg}[/white]")
                elif log_type == "WARN":
                    self.console.print(f"[orange3][{class_name}] : {msg}[/orange3]")
                elif log_type == "ALERT":
                    self.console.print(f"[red][{class_name}] : {msg}[/red]")
                elif log_type == "NOTIFY":
                    self.console.print(f"[cyan][{class_name}] : {msg}[/cyan]")
                else:
                    self.console.print(f"[white]{message}[/white]")
            else:
                self.console.print(f"[white]{message}[/white]")
                
        except Exception as e:
            self.console.print(f"[red]Error parsing message: {e}[/red]")
            self.console.print(f"[white]Raw message: {message}[/white]")
    
    def cleanup(self):
        self.running = False
        if self.socket:
            self.socket.close()
        self.console.print("[yellow]Disconnected[/yellow]")

def main():
    parser = argparse.ArgumentParser(description='Network Console Receiver')
    parser.add_argument('--connect', default='192.168.1.100', help='Local IP address to connect to (default: 192.168.1.100)')
    parser.add_argument('--port', type=int, default=8888, help='Port to connect to (default: 8888)')
    
    args = parser.parse_args()
    
    receiver = NetworkReceiver(args.connect, args.port)
    
    try:
        receiver.start()
    except KeyboardInterrupt:
        receiver.console.print("\n[yellow]Shutting down...[/yellow]")
        receiver.cleanup()

if __name__ == "__main__":
    main()

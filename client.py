#!/usr/bin/env python3
"""
Client that connects to the console stream server and displays output.
"""

import socket
import threading
import sys
import time
import argparse
from datetime import datetime

class ConsoleStreamClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = False
        
    def connect(self):
        """Connect to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout for connection
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.running = True
            
            print(f"Connected to server at {self.host}:{self.port}")
            print("Receiving console stream... (Press Ctrl+C to disconnect)")
            print("-" * 50)
            
            return True
            
        except socket.timeout:
            print(f"Connection timeout: Could not connect to {self.host}:{self.port}")
            return False
        except ConnectionRefusedError:
            print(f"Connection refused: Server at {self.host}:{self.port} is not running")
            return False
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def receive_messages(self):
        """Receive and display messages from the server."""
        try:
            while self.running and self.connected:
                try:
                    # Receive data from server
                    data = self.socket.recv(1024)
                    
                    if not data:
                        print("Server disconnected")
                        break
                    
                    # Decode and display the message
                    message = data.decode('utf-8').strip()
                    
                    # Skip ping messages (optional - remove this if you want to see pings)
                    if message == "PING":
                        continue
                    
                    # Display the message with timestamp
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] {message}")
                    
                except socket.timeout:
                    # No data received within timeout, continue
                    continue
                except socket.error as e:
                    print(f"Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"Error receiving messages: {e}")
        finally:
            self.disconnect()
    
    def send_message(self, message):
        """Send a message to the server (if server supports it)."""
        if self.connected and self.socket:
            try:
                self.socket.send(f"{message}\n".encode('utf-8'))
                return True
            except Exception as e:
                print(f"Error sending message: {e}")
                return False
        return False
    
    def disconnect(self):
        """Disconnect from the server."""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("\nDisconnected from server")
    
    def run(self):
        """Main client loop."""
        if not self.connect():
            return
        
        try:
            # Start receiving messages
            self.receive_messages()
            
        except KeyboardInterrupt:
            print("\nDisconnecting...")
            self.disconnect()

def scan_for_servers(port=8888, timeout=1):
    """Scan the local network for available servers."""
    import ipaddress
    
    # Get local network range
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Get network range (assuming /24 subnet)
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        
        print(f"Scanning network {network} for servers on port {port}...")
        
        servers = []
        for ip in network.hosts():
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(timeout)
                result = test_socket.connect_ex((str(ip), port))
                test_socket.close()
                
                if result == 0:
                    servers.append(str(ip))
                    print(f"Found server at {ip}:{port}")
                    
            except:
                continue
        
        return servers
        
    except Exception as e:
        print(f"Error scanning network: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Console Stream Client')
    parser.add_argument('--host', default='localhost', 
                       help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8888,
                       help='Server port (default: 8888)')
    parser.add_argument('--scan', action='store_true',
                       help='Scan local network for servers')
    
    args = parser.parse_args()
    
    if args.scan:
        servers = scan_for_servers(args.port)
        if servers:
            print(f"\nFound {len(servers)} server(s). You can connect using:")
            for server in servers:
                print(f"  python client.py --host {server}")
        else:
            print("No servers found on the local network.")
        return
    
    print("Console Stream Client")
    print("=" * 30)
    
    client = ConsoleStreamClient(host=args.host, port=args.port)
    
    try:
        client.run()
    except Exception as e:
        print(f"Client error: {e}")

if __name__ == "__main__":
    main()

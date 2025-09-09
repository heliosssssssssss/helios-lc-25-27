import socket
import threading
import sys
import argparse
from outbound import Outbound

class LogClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = False
        self.logger = Outbound(True, False)
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.running = True
            
            self.logger.success("CLIENT", f"Connected to {self.host}:{self.port}")
            return True
            
        except socket.timeout:
            self.logger.error("CLIENT", f"Connection timeout to {self.host}:{self.port}")
            return False
        except ConnectionRefusedError:
            self.logger.error("CLIENT", f"Connection refused to {self.host}:{self.port}")
            return False
        except Exception as e:
            self.logger.error("CLIENT", f"Connection error: {e}")
            return False
    
    def receive_messages(self):
        try:
            while self.running and self.connected:
                try:
                    data = self.socket.recv(1024)
                    
                    if not data:
                        self.logger.warn("CLIENT", "Server disconnected")
                        break
                    
                    message = data.decode('utf-8').strip()
                    print(message)
                    
                except socket.timeout:
                    continue
                except socket.error as e:
                    self.logger.error("CLIENT", f"Socket error: {e}")
                    break
                    
        except Exception as e:
            self.logger.error("CLIENT", f"Receive error: {e}")
        finally:
            self.disconnect()
    
    def disconnect(self):
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.logger.warn("CLIENT", "Disconnected from server")
    
    def run(self):
        if not self.connect():
            return
        
        try:
            self.receive_messages()
        except KeyboardInterrupt:
            self.logger.warn("CLIENT", "Disconnecting...")
            self.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8888, help='Server port')
    
    args = parser.parse_args()
    
    client = LogClient(host=args.host, port=args.port)
    
    try:
        client.run()
    except Exception as e:
        print(f"Client error: {e}")

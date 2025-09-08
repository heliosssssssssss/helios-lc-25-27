import os
import sys
import subprocess
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))
from console import console

class MainMenu:
    def __init__(self):
        self.transmit_process = None
        self.receive_process = None
        self.webcam_process = None
        self.receiver_debug_running = False
        
    def show_menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 50)
        print("           RT-OCR Control Panel")
        print("=" * 50)
        print()
        print("[1] : Transmit")
        print("[2] : Receive") 
        print("[3] : Receiver Debug")
        print("[4] : Begin Webcam")
        print("[5] : Exit")
        print()
        print("=" * 50)
        print("STATUS:")
        print(f"Transmit: {'RUNNING' if self.transmit_process and self.transmit_process.poll() is None else 'STOPPED'}")
        print(f"Receive:  {'RUNNING' if self.receive_process and self.receive_process.poll() is None else 'STOPPED'}")
        print(f"Debug:    {'RUNNING' if self.receiver_debug_running else 'STOPPED'}")
        print(f"Webcam:   {'RUNNING' if self.webcam_process and self.webcam_process.poll() is None else 'STOPPED'}")
        print("=" * 50)
        
    def transmit(self):
        if self.transmit_process and self.transmit_process.poll() is None:
            console.warn("Main", "Transmit already running")
            return
            
        console.log("Main", "Starting transmitter...")
        self.transmit_process = subprocess.Popen([sys.executable, "helpers/transmit.py"], 
                                                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        console.notify("Main", "Transmitter started in new window")
        
    def receive(self):
        if self.receive_process and self.receive_process.poll() is None:
            console.warn("Main", "Receive already running")
            return
            
        console.log("Main", "Starting receiver...")
        self.receive_process = subprocess.Popen([sys.executable, "helpers/receive.py"],
                                               creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        console.notify("Main", "Receiver started in new window")
        
    def receiver_debug(self):
        if self.receiver_debug_running:
            console.warn("Main", "Receiver debug already running")
            return
            
        console.log("Main", "Starting receiver debug in same window...")
        self.receiver_debug_running = True
        
        try:
            from helpers.receive import Receiver
            transmitter_ip = input("Enter transmitter machine IP address: ").strip()
            if not transmitter_ip:
                console.alert("Main", "No IP address provided")
                return
            receiver = Receiver(transmitter_ip)
            receiver.connect_to_server()
        except Exception as e:
            console.alert("Main", f"Receiver debug error: {e}")
        finally:
            self.receiver_debug_running = False
        
    def begin_webcam(self):
        if self.webcam_process and self.webcam_process.poll() is None:
            console.warn("Main", "Webcam already running")
            return
            
        console.log("Main", "Starting webcam...")
        self.webcam_process = subprocess.Popen([sys.executable, "core-sub/webcam_viewer.py"],
                                              creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        console.notify("Main", "Webcam started in new window")
        
    def cleanup(self):
        if self.transmit_process:
            self.transmit_process.terminate()
        if self.receive_process:
            self.receive_process.terminate()
        if self.webcam_process:
            self.webcam_process.terminate()
        console.log("Main", "All processes terminated")
        
    def run(self):
        while True:
            self.show_menu()
            choice = input("Select option: ").strip()
            
            if choice == "1":
                self.transmit()
            elif choice == "2":
                self.receive()
            elif choice == "3":
                self.receiver_debug()
            elif choice == "4":
                self.begin_webcam()
            elif choice == "5":
                self.cleanup()
                break
            else:
                console.alert("Main", "Invalid option")
                
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        menu = MainMenu()
        menu.run()
    except KeyboardInterrupt:
        console.warn("Main", "Interrupted by user")
    except Exception as e:
        console.alert("Main", f"Error: {e}")

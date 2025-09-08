import cv2
import sys
from console import ConsoleLogger

class WebcamManager:
    
    def __init__(self, camera_index=0, target_width=1920, target_height=1080, enable_network=False, network_host='localhost'):
        self.camera_index = camera_index
        self.target_width = target_width
        self.target_height = target_height
        self.window_name = "Webcam Feed - Fullscreen"
        self.quit_key = 'q'
        self.escape_key = 27
        
        self.cap = None
        self.is_running = False
        self.fps_target = 30
        
        self.console = ConsoleLogger(enable_network=enable_network, network_host=network_host)
        self.console.log("WebcamManager", "Initialized with camera index " + str(camera_index))
        
    def initialize_camera(self):
        try:
            self.console.log("WebcamManager", "Attempting to initialize camera...")
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                self.console.alert("WebcamManager", "Failed to open camera at index " + str(self.camera_index))
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps_target)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            self.console.notify("WebcamManager", f"Camera ready - Resolution: {actual_width}x{actual_height}, FPS: {actual_fps}")
            return True
            
        except Exception as e:
            self.console.alert("WebcamManager", "Exception during camera initialization: " + str(e))
            return False
    
    def setup_fullscreen_window(self):
        self.console.log("WebcamManager", "Setting up fullscreen window...")
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        self.console.notify("WebcamManager", "Fullscreen window ready")
    
    def process_frame(self, frame):
        return cv2.resize(frame, (self.target_width, self.target_height))
    
    def run(self):
        if not self.initialize_camera():
            return False
        
        self.setup_fullscreen_window()
        self.is_running = True
        self.console.notify("WebcamManager", "Starting webcam feed - Press 'q' or ESC to quit")
        
        try:
            while self.is_running:
                ret, frame = self.cap.read()
                
                if not ret:
                    self.console.warn("WebcamManager", "Failed to read frame from camera")
                    break
                
                processed_frame = self.process_frame(frame)
                cv2.imshow(self.window_name, processed_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(self.quit_key) or key == self.escape_key:
                    self.console.log("WebcamManager", "Quit key pressed, shutting down...")
                    break
                    
        except KeyboardInterrupt:
            self.console.warn("WebcamManager", "Program interrupted by user")
        except Exception as e:
            self.console.alert("WebcamManager", "Exception during execution: " + str(e))
        finally:
            self.cleanup()
        
        return True
    
    def cleanup(self):
        self.is_running = False
        
        if self.cap is not None:
            self.cap.release()
        
        cv2.destroyAllWindows()
        self.console.log("WebcamManager", "Cleanup completed successfully")

def main():
    try:
        self.console = ConsoleLogger(enable_network=True, network_host='192.168.1.100')  # Change to your laptop's IP
        self.console.log("Main", "Starting webcam application with network logging...")
        
        webcam_manager = WebcamManager(
            camera_index=0,
            target_width=1920,
            target_height=1080,
            enable_network=True,
            network_host='192.168.1.100'  # Change to your laptop's IP
        )
        
        webcam_manager.run()
        self.console.notify("Main", "Application completed successfully")
        
    except Exception as e:
        self.console.alert("Main", "Fatal error: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()

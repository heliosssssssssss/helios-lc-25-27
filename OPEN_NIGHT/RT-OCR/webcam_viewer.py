import cv2
import sys
from outbound import Outbound

class WebcamManager:
    
    def __init__(self, camera_index=0, target_width=1920, target_height=1080):
        self.camera_index = camera_index
        self.target_width = target_width
        self.target_height = target_height
        self.window_name = "Webcam Feed - Fullscreen"
        self.quit_key = 'q'
        self.escape_key = 27
        
        self.cap = None
        self.is_running = False
        self.fps_target = 30
        
        self.out = Outbound(True, True)
        
    def initialize_camera(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                self.out.error("WEBCAM", "Failed to open camera")
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps_target)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            self.out.success("WEBCAM", f"Camera initialized at {self.target_width}x{self.target_height}")
            return True
            
        except Exception as e:
            self.out.error("WEBCAM", f"Camera initialization failed: {e}")
            return False
    
    def setup_fullscreen_window(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    def process_frame(self, frame):
        return cv2.resize(frame, (self.target_width, self.target_height))
    
    def run(self):
        if not self.initialize_camera():
            return False
        
        self.setup_fullscreen_window()
        self.is_running = True
        self.out.success("WEBCAM", "Webcam viewer started")
        
        try:
            while self.is_running:
                ret, frame = self.cap.read()
                
                if not ret:
                    self.out.warn("WEBCAM", "Failed to read frame")
                    break
                
                processed_frame = self.process_frame(frame)
                cv2.imshow(self.window_name, processed_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(self.quit_key) or key == self.escape_key:
                    self.out.log("WEBCAM", "User requested exit")
                    break
                    
        except KeyboardInterrupt:
            self.out.warn("WEBCAM", "Interrupted by user")
        except Exception as e:
            self.out.error("WEBCAM", f"Runtime error: {e}")
        finally:
            self.cleanup()
        
        return True
    
    def cleanup(self):
        self.is_running = False
        
        if self.cap is not None:
            self.cap.release()
        
        cv2.destroyAllWindows()
        self.out.warn("WEBCAM", "Webcam viewer stopped")

def main():
    try:
        webcam_manager = WebcamManager(
            camera_index=0,
            target_width=1920,
            target_height=1080
        )
        
        webcam_manager.run()
        
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    main()
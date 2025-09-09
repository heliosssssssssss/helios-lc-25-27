import cv2
from outbound import Outbound

class WebcamManager:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.out = Outbound(True, True)
        
    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            self.out.error("WEBCAM", "Camera failed")
            return
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        self.out.success("WEBCAM", "Started")
        
        cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Webcam", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                self.out.warn("WEBCAM", "No frame")
                break
            
            cv2.imshow("Webcam", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        self.out.warn("WEBCAM", "Stopped")

if __name__ == "__main__":
    WebcamManager().start()
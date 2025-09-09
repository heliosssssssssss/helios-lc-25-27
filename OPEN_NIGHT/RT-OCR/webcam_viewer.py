import cv2
import numpy as np
from outbound import Outbound
from ocr_model import OCRv1

class DrawManager:
    def __init__(self):
        self.out = Outbound(True, True)
        
    def draw_boxes(self, frame, boxes):
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        return frame

class WebcamManager:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.out = Outbound(True, True)
        self.draw_manager = DrawManager()
        self.ocr = OCRv1()
        self.prev_frame = None
        
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
            
            if self.prev_frame is not None:
                boxes = self.ocr.detect_movement(self.prev_frame, frame)
                frame = self.draw_manager.draw_boxes(frame, boxes)
            
            self.prev_frame = frame.copy()
            cv2.imshow("Webcam", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        self.out.warn("WEBCAM", "Stopped")

if __name__ == "__main__":
    WebcamManager().start()
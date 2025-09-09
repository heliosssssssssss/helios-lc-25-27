import cv2
from outbound import Outbound
from ocr_model import TextDetector

class WebcamManager:
    def __init__(self, camera_index=0, enable_ocr=False, target_word="chicken", detect_all_text=False):
        self.out = Outbound(True, True)
        self.out.log("WEBCAM", "initializing webcam manager...")
        
        self.camera_index = camera_index
        self.cap = None
        self.enable_ocr = enable_ocr
        self.target_word = target_word
        self.detect_all_text = detect_all_text
        self.ocr_detector = None
        
        self.out.info("WEBCAM", f"camera index: {self.camera_index}")
        self.out.info("WEBCAM", f"ocr enabled: {self.enable_ocr}")
        if self.enable_ocr:
            self.out.info("WEBCAM", f"target word: '{self.target_word}'")
            self.out.info("WEBCAM", f"detect all text: {self.detect_all_text}")
            self.out.log("WEBCAM", "creating ocr detector...")
            self.ocr_detector = TextDetector(target_word=target_word, camera_index=camera_index, detect_all_text=detect_all_text)
            self.out.success("WEBCAM", "ocr detector created")
        else:
            self.out.info("WEBCAM", "simple webcam mode")
        
    def start(self):
        self.out.log("WEBCAM", "starting webcam...")
        if self.enable_ocr and self.ocr_detector:
            self.out.info("WEBCAM", "using ocr detector")
            self.ocr_detector.start()
        else:
            self.out.info("WEBCAM", "using simple webcam mode")
            self.out.log("WEBCAM", f"opening camera {self.camera_index}")
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                self.out.error("WEBCAM", "camera failed")
                return
            
            self.out.success("WEBCAM", "camera opened")
            self.out.log("WEBCAM", "setting camera properties...")
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            
            actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.out.info("WEBCAM", f"actual resolution: {int(actual_width)}x{int(actual_height)}")
            
            self.out.success("WEBCAM", "started")
            self.out.log("WEBCAM", "creating fullscreen window...")
            
            cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Webcam", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
            frame_count = 0
            self.out.log("WEBCAM", "entering main loop...")
            while True:
                ret, frame = self.cap.read()
                frame_count += 1
                
                if not ret:
                    self.out.warn("WEBCAM", "bad frame")
                    break
                
                if frame_count % 30 == 0:
                    self.out.log("WEBCAM", f"processed {frame_count} frames")
                
                cv2.imshow("Webcam", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.out.info("WEBCAM", "quitting...")
                    break
            
            self.out.log("WEBCAM", "releasing camera...")
            self.cap.release()
            cv2.destroyAllWindows()
            self.out.warn("WEBCAM", "stopped")

if __name__ == "__main__":
    out = Outbound(True, True)
    out.log("MAIN", "starting webcam viewer application")
    out.info("MAIN", "available modes:")
    out.info("MAIN", "1: simple webcam")
    out.info("MAIN", "2: webcam with ocr")
    out.info("MAIN", "3: webcam detect all text")
    
    print("webcam viewer")
    print("1: simple webcam")
    print("2: webcam with ocr")
    print("3: webcam detect all text")

    print("HEY - WEBCAM_3 HAS BEEN DISABLED BY HELIOS - HEY")
    choice = input("pick one: ").strip()
    
    out.log("MAIN", f"user selected option: {choice}")
    
    if choice == "2":
        out.log("MAIN", "ocr mode selected")
        target = input("what word to find (default chicken): ").strip()
        if not target:
            target = "chicken"
        out.info("MAIN", f"target word: '{target}'")
        WebcamManager(enable_ocr=True, target_word=target).start()
    elif choice == "3":
        out.log("MAIN", "detect all text mode selected")
        WebcamManager(enable_ocr=True, detect_all_text=True).start()
    else:
        out.log("MAIN", "simple webcam mode selected")
        WebcamManager().start()
    
    out.success("MAIN", "application completed")
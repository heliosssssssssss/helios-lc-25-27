import cv2
from outbound import Outbound
from ocr_model import TextDetector

## HEY ! HEY ! [THIS IS A HELIOS INTERNATIONAL PROJECT | OPEN NIGHT 2025]

## [+] This project is outlined under no liscence, however falls under the h1k.org private Github, view h1k.org/git-redis/en for further)

#####################

## PROJECT OUTLINE
## THIS IS A HELIOS INTERNATIONAL PROJECT | OPEN NIGHT 2025 (SPECIAL THANKS TO PIOTR)
## Known issues (including model)
## 1. Server stream where (server) quits/exit, (client/s) receive a error, rather an error handeled msg 
## 2. I tested local stream (using Source Local Send method) on school network, looks fine to me but im unsure still (TBE)
## 3. OCR blue index appears to glitch out after 10 detections in rapid motion, box remains on UI frontend forever
## 4. sometimes the outbound has a formatting issue, ive seen it so far in print statements containing special characters, idk why but a fallback has been made (view fb2)

## SERVER.PY -> (CBS PC W/ WEBCAM)
## CLIENT.PY -> (LAPTOP W/ CMD) 
## OUTBOUND.PY -> (GLOBAL UTIL FOR FORMAT LOGS) 
## OCR_MODEL.PY -> (OCR MODEL FOR ENGLISH WORDS - BY PZ)

# webcam viewer -> (acts as main.py imo) -> develped by heliosfr (07/09/2025)

class WebcamManager:
    def __init__(self, camera_index=0, enable_ocr=False, target_word="chicken", detect_all_text=False, clean_mode=False):
        self.out = Outbound(True, True)
        self.out.log("WEBCAM", "initializing webcam manager...")
        
        self.camera_index = camera_index # default set 0 for webcam, idk should b g
        self.cap = None #(capture obj)
        self.enable_ocr = enable_ocr
        self.target_word = target_word
        self.detect_all_text = detect_all_text
        self.clean_mode = clean_mode
        self.ocr_detector = None #TextDetector()
        
        self.out.info("WEBCAM", f"camera index: {self.camera_index}")
        self.out.info("WEBCAM", f"ocr enabled: {self.enable_ocr}")
        if self.enable_ocr:
            self.out.info("WEBCAM", f"target word: '{self.target_word}'")
            self.out.info("WEBCAM", f"detect all text: {self.detect_all_text}")
            self.out.info("WEBCAM", f"clean mode: {self.clean_mode}")
            self.out.log("WEBCAM", "creating ocr detector...")
            self.ocr_detector = TextDetector(target_word=target_word, camera_index=camera_index, detect_all_text=detect_all_text, clean_mode=clean_mode)
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
            self.cap = cv2.VideoCapture(self.camera_index) # origin 1
            
            if not self.cap.isOpened():
                self.out.error("WEBCAM", "camera failed")
                return
            
            self.out.success("WEBCAM", "camera opened")
            self.out.log("WEBCAM", "setting camera properties...")
            
            #self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
            #self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            
            actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.out.info("WEBCAM", f"actual resolution: {int(actual_width)}x{int(actual_height)}")
            
            self.out.success("WEBCAM", "started")
            self.out.log("WEBCAM", "creating fullscreen window...")
            
            cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Webcam", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
            frame_count = 0 # (below is frame limit check and count1)
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
    
    print("webcam viewer")
    print("1: simple webcam") # without ocr 
    print("2: webcam with ocr") # uses piotr's ocr model
    print("3: webcam detect all text") # disabled, requires intense CUDA utilization which i or school dont got 
    print("4: clean ocr mode (no debug overlays)") # option 2 without debug and motion debug

    print("HEY - WEBCAM_3 HAS BEEN DISABLED BY HELIOS - HEY")
    choice = input("pick one: ").strip()
    
    out.log("MAIN", f"user selected option: {choice}") # outbound for debug
    
    ## choices
    if choice == "2":
        out.log("MAIN", "ocr mode selected")
        target = input("what word to find (default chicken): ").strip()
        if not target:
            target = "chicken" # default 
        out.info("MAIN", f"target word: '{target}'")
        WebcamManager(enable_ocr=True, target_word=target).start()
    elif choice == "3":
        out.log("MAIN", "detect all text mode selected")
        WebcamManager(enable_ocr=True, detect_all_text=True).start()
    elif choice == "4":
        out.log("MAIN", "clean ocr mode selected")
        target = input("what word to find (default chicken): ").strip()
        if not target:
            target = "chicken"
        out.info("MAIN", f"clean mode target: '{target}'")
        WebcamManager(enable_ocr=True, target_word=target, clean_mode=True).start()
    else:
        out.log("MAIN", "simple webcam mode selected")
        WebcamManager().start()
    
    out.success("MAIN", "application completed")


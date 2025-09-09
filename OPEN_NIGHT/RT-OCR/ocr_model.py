import numpy as np
import cv2
import pyautogui
import time
from threading import Thread, Lock
import easyocr
import re
import torch
from outbound import Outbound

## HEY ! HEY ! [THIS IS A HELIOS INTERNATIONAL PROJECT | OPEN NIGHT 2025]

# MADE BY Piotr Stelmaszek (University College Cork, UCC - 2024/2025) 
# CHANGES 09/*/25 -> INTEGRATION TO WEBCAM_VIEWER, SLIGHT OPTIMISATIONS FOR NON-CUDA, AND OUTBOUND

## Opt1 -> Check for motion in predict range, (post-red check, priority set to low) for example vertical motion can
# be determined from pixel difference and the direction in which change occurs. Increase range, in X direction 

## adjusted for webcam_viewer.py integration (08/09/25)

## REVISIONAL NOTES, -> FROM PIOTR
# the ocr detection works by actively calculating only in ROIs for performance, it uses a predefined model by easyocr 
# originally i was going to use pytescr but easyocr was more lightweight and more efficient




class TextDetector:
    def __init__(self, target_word="chicken", fps=30, camera_index=0, detect_all_text=False, clean_mode=False):
        self.out = Outbound(True, True)
        self.out.log("OCR", "initializing text detector...")
        
        self.fps = fps
        self.recording = False
        self.frame = None
        self.target_word = target_word.lower()
        self.detect_all_text = detect_all_text
        self.clean_mode = clean_mode
        self.ocr_result = (False, 0, [], 0.0)
        self.frame_count = 0
        self.ocr_interval = 1
        self.scale_factor = 0.7
        self.lock = Lock()
        self.detected_areas = []
        self.area_persistence = 0.1
        self.roi_expansion = 2.0
        self.trail_points = []
        self.trail_persistence = 2.0
        self.prev_blue_centers = []
        self.last_detection_time = 0
        self.processing_queue = []
        self.max_queue_size = 3
        self.skip_frames = 0
        self.last_valid_box = None
        self.box_velocity = None
        self.last_box_time = 0
        self.ocr_pending = False
        self.ocr_thread = None
        self.camera_index = camera_index
        self.cap = None
        
        self.out.info("OCR", f"target: '{self.target_word}' detect_all: {self.detect_all_text} clean: {self.clean_mode}")
        self.motion_vector_interval = 3
        self.show_motion_vectors = True
        self.motion_grid_step = 40
        self.min_motion_magnitude = 8
        self.brightness_threshold = 245
        self.exposure_compensation = 1.0
        self.max_exposure_compensation = 0.2
        self.min_exposure_compensation = 1.0
        self.exposure_adjustment_speed = 0.2
        self.brightness_history = []
        self.brightness_history_size = 5
        
        if torch.cuda.is_available():
            self.out.success("OCR", "gpu detected, gonna be fast")
            self.fast_reader = easyocr.Reader(
                ['en'], 
                gpu=True,
                model_storage_directory='./fast_ocr',
                download_enabled=True,
                quantize=True,
                verbose=False
            )
            self.reader = self.fast_reader
        else:
            self.out.warn("OCR", "no gpu found, might be slow")
            self.fast_reader = easyocr.Reader(['en'], gpu=True, verbose=False)
            self.reader = self.fast_reader

    def start(self):
        self.out.info("OCR", "starting up...")
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            self.out.error("OCR", "camera not working")
            return
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.out.success("OCR", f"ready - resolution: {int(actual_width)}x{int(actual_height)}")
        
        cv2.namedWindow("Webcam OCR", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Webcam OCR", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        self.recording = True
        self._process_webcam_integrated()

    def start_screen_recording(self):
        self.recording = True
        Thread(target=self._process_screen).start()

    def start_webcam_recording(self):
        self.recording = True
        Thread(target=self._process_webcam).start()

    def stop_recording(self):
        self.recording = False

    def _calculate_motion_vectors(self, prev_gray, current_gray, min_magnitude=8):
        if prev_gray is None or current_gray is None:
            return []
            
        scale = 0.5
        h, w = prev_gray.shape
        small_h, small_w = int(h * scale), int(w * scale)
        prev_small = cv2.resize(prev_gray, (small_w, small_h))
        curr_small = cv2.resize(current_gray, (small_w, small_h))
        
        flow = cv2.calcOpticalFlowFarneback(
            prev_small, curr_small, 
            None,
            0.5,
            2,
            10,
            2,
            5,
            1.2,
            0
        )
        
        vectors = []
        for y in range(0, small_h, self.motion_grid_step):
            for x in range(0, small_w, self.motion_grid_step):
                fx, fy = flow[y, x]
                magnitude = np.sqrt(fx*fx + fy*fy)
                
                if magnitude > min_magnitude:
                    orig_x = int(x / scale)
                    orig_y = int(y / scale)
                    end_x = int((x + fx) / scale)
                    end_y = int((y + fy) / scale)
                    
                    vectors.append({
                        'start': (orig_x, orig_y),
                        'end': (end_x, end_y),
                        'magnitude': magnitude
                    })
        
        return vectors

    def _draw_motion(self, frame, prev_gray, min_area=500):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        motion_boxes = []
        
        if prev_gray is not None:
            if not self.clean_mode and self.show_motion_vectors and self.frame_count % self.motion_vector_interval == 0:
                motion_vectors = self._calculate_motion_vectors(prev_gray, gray, self.min_motion_magnitude)
                if len(motion_vectors) > 0:
                    self.out.info("MOTION", f"found {len(motion_vectors)} motion vectors")
                
                for i, vec in enumerate(motion_vectors):
                    start = vec['start']
                    end = vec['end']
                    magnitude = vec['magnitude']
                    
                    color = (0, 0, 255)
                    if magnitude < 10:
                        color = (0, 255, 0)
                    elif magnitude < 20:
                        color = (0, 255, 255)
                    
                    cv2.arrowedLine(frame, start, end, color, 1, tipLength=0.2)
            
            frame_delta = cv2.absdiff(prev_gray, gray)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            grouped_boxes = []
            for c in contours:
                area = cv2.contourArea(c)
                if area < min_area:
                    continue
                (x, y, w, h) = cv2.boundingRect(c)
                grouped_boxes.append((x, y, w, h))
            
            if grouped_boxes:
                merged_boxes = []
                current_box = list(grouped_boxes[0])
                
                for box in grouped_boxes[1:]:
                    x, y, w, h = box
                    if (abs(current_box[0] - x) < 50 and abs(current_box[1] - y) < 50):
                        x1 = min(current_box[0], x)
                        y1 = min(current_box[1], y)
                        x2 = max(current_box[0] + current_box[2], x + w)
                        y2 = max(current_box[1] + current_box[3], y + h)
                        current_box = [x1, y1, x2 - x1, y2 - y1]
                    else:
                        merged_boxes.append(tuple(current_box))
                        current_box = list(box)
                merged_boxes.append(tuple(current_box))
                
                for (x, y, w, h) in merged_boxes:
                    motion_boxes.append((x, y, w, h))
                    if not self.clean_mode:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                
                if len(motion_boxes) > 0 and not self.clean_mode:
                    self.out.success("MOTION", f"found {len(motion_boxes)} motion boxes")
                
                if len(merged_boxes) > 1 and not self.clean_mode:
                    centers = [(x + w//2, y + h//2) for (x, y, w, h) in merged_boxes]
                    centers.sort(key=lambda x: x[0])
                    
                    overlay = frame.copy()
                    for i in range(len(centers) - 1):
                        pt1 = centers[i]
                        pt2 = centers[i + 1]
                        cv2.line(overlay, pt1, pt2, (0, 165, 255), 2)
                        cv2.circle(overlay, pt1, 4, (0, 165, 255), -1)
                        cv2.circle(overlay, pt2, 4, (0, 165, 255), -1)
                    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        return gray, frame, motion_boxes

    def _update_detected_areas(self, boxes):
        now = time.time()
        
        if not boxes:
            time_since_last_detection = now - self.last_detection_time
            if time_since_last_detection > self.area_persistence:
                if len(self.detected_areas) > 0:
                    self.out.info("OCR", "no more text, clearing boxes")
                self.detected_areas = []
                return
        
        if boxes:
            self.last_detection_time = now
            for box in boxes:
                pts = np.array(box)
                center = np.mean(pts, axis=0)
                width = np.max(pts[:, 0]) - np.min(pts[:, 0])
                height = np.max(pts[:, 1]) - np.min(pts[:, 1])
                new_width = width * self.roi_expansion
                new_height = height * self.roi_expansion
                x1 = int(center[0] - new_width/2)
                y1 = int(center[1] - new_height/2)
                x2 = int(center[0] + new_width/2)
                y2 = int(center[1] + new_height/2)
                expanded_box = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                self.detected_areas.append((expanded_box, now, center))
                self.trail_points.append((center, now))
                self.prev_blue_centers.append(center)
        
        self.detected_areas = [(box, timestamp, center) for box, timestamp, center in self.detected_areas 
                             if now - timestamp < self.area_persistence]
        
        active_centers = set(tuple(center) for _, _, center in self.detected_areas)
        self.trail_points = [(point, timestamp) for point, timestamp in self.trail_points 
                           if now - timestamp < self.trail_persistence and tuple(point) in active_centers]
        
        if len(self.detected_areas) > 1:
            merged_areas = []
            current_area = list(self.detected_areas[0])
            for area in self.detected_areas[1:]:
                box1 = np.array(current_area[0])
                box2 = np.array(area[0])
                x1 = max(np.min(box1[:, 0]), np.min(box2[:, 0]))
                y1 = max(np.min(box1[:, 1]), np.min(box2[:, 1]))
                x2 = min(np.max(box1[:, 0]), np.max(box2[:, 0]))
                y2 = min(np.max(box1[:, 1]), np.max(box2[:, 1]))
                if x1 < x2 and y1 < y2:
                    merged_box = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                    current_area = (merged_box, max(current_area[1], area[1]), current_area[2])
                else:
                    merged_areas.append(current_area)
                    current_area = list(area)
            merged_areas.append(current_area)
            self.detected_areas = merged_areas

    def _adjust_brightness(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2]
        avg_brightness = np.mean(v_channel)
        
        _, bright_mask = cv2.threshold(v_channel, self.brightness_threshold, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        adjusted = frame.copy()
        exposure_values = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                region_brightness = np.mean(v_channel[y:y+h, x:x+w])
                compensation = max(0.6, min(0.8, 1.0 - (region_brightness - self.brightness_threshold) / 255.0))
                exposure_values.append(compensation)
                roi = adjusted[y:y+h, x:x+w]
                roi = cv2.convertScaleAbs(roi, alpha=compensation, beta=0)
                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                roi = cv2.filter2D(roi, -1, kernel)
                adjusted[y:y+h, x:x+w] = roi
        
        avg_exposure = np.mean(exposure_values) if exposure_values else 1.0
        if len(contours) > 0:
            self.out.info("BRIGHT", f"brightness: {avg_brightness:.1f} regions: {len(contours)} comp: {avg_exposure:.2f}")
        cv2.putText(adjusted, f"Brightness: {avg_brightness:.1f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(adjusted, f"Average Exposure Debug: {avg_exposure:.2f}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        return adjusted

    def _preprocess_roi(self, roi):
        roi = self._adjust_brightness(roi)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        sharp = cv2.filter2D(gray, -1, kernel)
        contrast = cv2.convertScaleAbs(sharp, alpha=1.5, beta=0)
        thresh = cv2.adaptiveThreshold(contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    def _preprocess_roi_fast(self, roi):
        if roi.size == 0:
            return None
        
        roi = self._adjust_brightness(roi)
        h, w = roi.shape[:2]
        expand = 0.2
        new_h = int(h * (1 + expand))
        new_w = int(w * (1 + expand))
        center_y, center_x = h // 2, w // 2
        y1 = max(0, center_y - new_h // 2)
        y2 = min(h, center_y + new_h // 2)
        x1 = max(0, center_x - new_w // 2)
        x2 = min(w, center_x + new_w // 2)
        roi = roi[y1:y2, x1:x2]
        
        h, w = roi.shape[:2]
        new_h = min(h, 100)
        scale = new_h / h
        new_w = int(w * scale)
        roi = cv2.resize(roi, (new_w, new_h))
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        blur = cv2.GaussianBlur(thresh, (3, 3), 0)
        sharp = cv2.addWeighted(thresh, 1.5, blur, -0.5, 0)
        return cv2.cvtColor(sharp, cv2.COLOR_GRAY2BGR)

    def _predict_next_box(self, current_time):
        if self.last_valid_box is None or self.box_velocity is None:
            return None
            
        time_diff = current_time - self.last_box_time
        if time_diff > 0.5:
            return None
            
        predicted_box = []
        for point in self.last_valid_box:
            new_x = point[0] + self.box_velocity[0] * time_diff
            new_y = point[1] + self.box_velocity[1] * time_diff
            predicted_box.append((int(new_x), int(new_y)))
        
        return predicted_box

    def _update_box_velocity(self, new_box):
        if self.last_valid_box is None:
            self.last_valid_box = new_box
            self.last_box_time = time.time()
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_box_time
        if time_diff > 0:
            old_center = np.mean(self.last_valid_box, axis=0)
            new_center = np.mean(new_box, axis=0)
            
            velocity_x = (new_center[0] - old_center[0]) / time_diff
            velocity_y = (new_center[1] - old_center[1]) / time_diff
            
            if self.box_velocity is None:
                self.box_velocity = (velocity_x, velocity_y)
            else:
                self.box_velocity = (
                    0.7 * self.box_velocity[0] + 0.3 * velocity_x,
                    0.7 * self.box_velocity[1] + 0.3 * velocity_y
                )
            
            self.last_valid_box = new_box
            self.last_box_time = current_time

    def _ocr_worker(self, frame, motion_boxes):
        start_time = time.time()
        found = False
        word_count = 0
        if not self.detect_all_text:
            pattern = re.compile(rf'{re.escape(self.target_word)}', re.IGNORECASE)
        boxes = []
        max_confidence = 0.0
        predicted_box = self._predict_next_box(start_time)
        if predicted_box is not None:
            x_coords = [p[0] for p in predicted_box]
            y_coords = [p[1] for p in predicted_box]
            x1, x2 = min(x_coords), max(x_coords)
            y1, y2 = min(y_coords), max(y_coords)
            pad = 20
            x1 = max(0, x1 - pad)
            y1 = max(0, y1 - pad)
            x2 = min(frame.shape[1], x2 + pad)
            y2 = min(frame.shape[0], y2 + pad)
            roi_w = x2 - x1
            roi_h = y2 - y1
            expand = 0.2
            x1 = max(0, int(x1 - roi_w * expand / 2))
            y1 = max(0, int(y1 - roi_h * expand / 2))
            x2 = min(frame.shape[1], int(x2 + roi_w * expand / 2))
            y2 = min(frame.shape[0], int(y2 + roi_h * expand / 2))
            roi = frame[y1:y2, x1:x2]
            if roi.size > 0:
                roi_pre = self._preprocess_roi_fast(roi)
                if roi_pre is not None:
                    results = self.fast_reader.readtext(
                        roi_pre,
                        min_size=10,
                        width_ths=0.3,
                        paragraph=False,
                        batch_size=1
                    )
                    for i, (bbox, text, conf) in enumerate(results):
                        if self.detect_all_text or pattern.search(text):
                            found = True
                            word_count += 1
                            max_confidence = max(max_confidence, conf)
                            bbox_global = [(int(x1 + bx), int(y1 + by)) for (bx, by) in bbox]
                            boxes.append(bbox_global)
                            self.out.success("OCR", f"match! '{text}' conf: {conf:.2f}")
                            self._update_box_velocity(bbox_global)
                            if not self.detect_all_text:
                                break
        if not found:
            for i, (x, y, w, h) in enumerate(motion_boxes):
                expand = 0.2
                ex = int(w * expand / 2)
                ey = int(h * expand / 2)
                x1 = max(0, x - ex)
                y1 = max(0, y - ey)
                x2 = min(frame.shape[1], x + w + ex)
                y2 = min(frame.shape[0], y + h + ey)
                roi = frame[y1:y2, x1:x2]
                roi_pre = self._preprocess_roi_fast(roi)
                if roi_pre is not None:
                    results = self.fast_reader.readtext(
                        roi_pre,
                        min_size=10,
                        width_ths=0.3,
                        paragraph=False,
                        batch_size=1
                    )
                    for j, (bbox, text, conf) in enumerate(results):
                        if self.detect_all_text or pattern.search(text):
                            found = True
                            word_count += 1
                            max_confidence = max(max_confidence, conf)
                            bbox_global = [(int(x1 + bx), int(y1 + by)) for (bx, by) in bbox]
                            boxes.append(bbox_global)
                            self.out.success("OCR", f"match! '{text}' conf: {conf:.2f}")
                            self._update_box_velocity(bbox_global)
                            if not self.detect_all_text:
                                break
                if found:
                    break
        elapsed = time.time() - start_time
        if found:
            self.out.success("OCR", f"found {word_count} text regions in {elapsed:.2f}s")
        else:
            self.out.warn("OCR", f"no text found in {elapsed:.2f}s")
        self.last_ocr_time = elapsed
        with self.lock:
            self.ocr_result = (found, word_count, boxes, max_confidence)
            self.ocr_pending = False

    def _detect_bright_regions(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2]
        
        _, bright_mask = cv2.threshold(v_channel, self.brightness_threshold, 255, cv2.THRESH_BINARY)
        
        kernel = np.ones((5,5), np.uint8)
        bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)
        bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bright_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                x = max(0, x - 5)
                y = max(0, y - 5)
                w = min(frame.shape[1] - x, w + 10)
                h = min(frame.shape[0] - y, h + 10)
                bright_regions.append((x, y, w, h))
        
        if bright_regions:
            merged_regions = []
            current_region = list(bright_regions[0])
            
            for region in bright_regions[1:]:
                x, y, w, h = region
                if (abs(current_region[0] - x) < 50 and abs(current_region[1] - y) < 50):
                    x1 = min(current_region[0], x)
                    y1 = min(current_region[1], y)
                    x2 = max(current_region[0] + current_region[2], x + w)
                    y2 = max(current_region[1] + current_region[3], y + h)
                    current_region = [x1, y1, x2 - x1, y2 - y1]
                else:
                    merged_regions.append(tuple(current_region))
                    current_region = list(region)
            merged_regions.append(tuple(current_region))
            return merged_regions
        return []

    def _draw_boxes(self, frame, word_count, boxes, ocr_time=None, motion_box_count=None):
        if self.clean_mode:
            # Clean mode: show green text notification and highlight detected text
            if word_count > 0:
                cv2.putText(frame, f"Found '{self.target_word}'", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                # Highlight the detected text with green boxes
                for pts in boxes:
                    pts_np = np.array(pts, dtype=np.int32)
                    cv2.polylines(frame, [pts_np], isClosed=True, color=(0,255,0), thickness=4)
                    overlay = frame.copy()
                    cv2.fillPoly(overlay, [pts_np], (0,255,0))
                    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            return frame
        
        current_time = time.time()
        predicted_box = self._predict_next_box(current_time)
        if predicted_box is not None:
            pts_np = np.array(predicted_box, dtype=np.int32)
            cv2.polylines(frame, [pts_np], isClosed=True, color=(255,165,0), thickness=1)
        
        if motion_box_count and motion_box_count > 1:
            motion_centers = []
            for box, _, _ in self.detected_areas:
                center = np.mean(np.array(box), axis=0)
                motion_centers.append(center)
            
            if len(motion_centers) > 1:
                motion_centers.sort(key=lambda x: x[0])
                overlay = frame.copy()
                for i in range(len(motion_centers) - 1):
                    pt1 = motion_centers[i]
                    pt2 = motion_centers[i + 1]
                    cv2.line(overlay, 
                            (int(pt1[0]), int(pt1[1])),
                            (int(pt2[0]), int(pt2[1])),
                            (0, 165, 255), 2)
                    cv2.circle(overlay, (int(pt1[0]), int(pt1[1])), 4, (0, 165, 255), -1)
                    cv2.circle(overlay, (int(pt2[0]), int(pt2[1])), 4, (0, 165, 255), -1)
                cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        if len(self.prev_blue_centers) >= 2:
            pt1 = self.prev_blue_centers[-2]
            pt2 = self.prev_blue_centers[-1]
            cv2.line(frame, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])), (0, 255, 255), 4)
        
        for i, (box, _, _) in enumerate(self.detected_areas):
            pts_np = np.array(box, dtype=np.int32)
            overlay = frame.copy()
            if i == 0 and len(self.detected_areas) > 1:
                cv2.polylines(frame, [pts_np], isClosed=True, color=(180,0,80), thickness=1)
                cv2.fillPoly(overlay, [pts_np], (180,0,80))
                cv2.addWeighted(overlay, 0.05, frame, 0.95, 0, frame)
            else:
                cv2.polylines(frame, [pts_np], isClosed=True, color=(255,0,0), thickness=1)
                cv2.fillPoly(overlay, [pts_np], (255,0,0))
                cv2.addWeighted(overlay, 0.1, frame, 0.9, 0, frame)
        
        for pts in boxes:
            pts_np = np.array(pts, dtype=np.int32)
            cv2.polylines(frame, [pts_np], isClosed=True, color=(0,255,0), thickness=4)
            overlay = frame.copy()
            cv2.fillPoly(overlay, [pts_np], (0,255,0))
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        bright_regions = self._detect_bright_regions(frame)
        for (x, y, w, h) in bright_regions:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)

        if self.detect_all_text:
            if word_count > 0:
                cv2.putText(frame, f"Found {word_count} text regions", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "No text detected", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            if word_count > 0:
                cv2.putText(frame, f"Found {word_count} instances of '{self.target_word}'", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, f"Found no instances of '{self.target_word}'", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame, "By UCC-2024M-PSZ (UCC.IE - @2025)", 
                   (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Active tracking regions: {len(self.detected_areas)}", 
                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        if ocr_time is not None:
            cv2.putText(frame, f"OCR time: {ocr_time:.3f}s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        if motion_box_count is not None:
            cv2.putText(frame, f"Active motion boxes: {motion_box_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 128, 255), 2)
        
        with self.lock:
            _, _, _, confidence = self.ocr_result
            if confidence > 0:
                text = f"Confidence: {confidence:.2%}"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                x = frame.shape[1] - text_size[0] - 10
                y = 30
                cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        return frame

    def _process_frame_parallel(self, frame, motion_boxes):
        if len(self.processing_queue) < self.max_queue_size and not self.ocr_pending:
            self.ocr_pending = True
            thread = Thread(target=self._ocr_worker, args=(frame.copy(), motion_boxes))
            thread.start()
            self.processing_queue.append(thread)
            self.ocr_thread = thread
        else:
            self._cleanup_threads()
            if len(self.processing_queue) < self.max_queue_size and not self.ocr_pending:
                self.ocr_pending = True
                thread = Thread(target=self._ocr_worker, args=(frame.copy(), motion_boxes))
                thread.start()
                self.processing_queue.append(thread)
                self.ocr_thread = thread

    def _cleanup_threads(self):
        self.processing_queue = [t for t in self.processing_queue if t.is_alive()]

    def _process_screen(self):
        prev_gray = None
        while self.recording:
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            height, width = frame.shape[:2]
            new_height = int(height * self.scale_factor)
            new_width = int(width * self.scale_factor)
            frame = cv2.resize(frame, (new_width, new_height))
            
            self.frame_count += 1
            prev_gray, frame, motion_boxes = self._draw_motion(frame, prev_gray)
            
            if self.frame_count % self.ocr_interval == 0 and not self.ocr_pending:
                self._process_frame_parallel(frame, motion_boxes)
            
            self._cleanup_threads()
            
            with self.lock:
                found, word_count, boxes, confidence = self.ocr_result
                if found:
                    self._update_detected_areas(boxes)
            
            processed_frame = self._draw_boxes(frame, word_count, boxes, 
                                            getattr(self, 'last_ocr_time', None),
                                            len(motion_boxes))
            
            cv2.imshow('Text Detection Preview', processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.recording = False
                break
            
            if self.skip_frames > 0:
                time.sleep(1/(self.fps * 2))
            else:
                time.sleep(1/self.fps)
        
        cv2.destroyAllWindows()
        for thread in self.processing_queue:
            thread.join()

    def _process_webcam(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Could not open webcam.")
            self.recording = False
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        width = int(1920 * self.scale_factor)
        height = int(1080 * self.scale_factor)
        
        window_name = 'Webcam Text Detection'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, width, height)
        
        prev_gray = None
        while self.recording:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame from webcam.")
                break
            
            frame = cv2.resize(frame, (width, height))
            self.frame_count += 1
            prev_gray, frame, motion_boxes = self._draw_motion(frame, prev_gray)
            
            if self.frame_count % self.ocr_interval == 0 and not self.ocr_pending:
                self._process_frame_parallel(frame, motion_boxes)
            
            self._cleanup_threads()
            
            with self.lock:
                found, word_count, boxes, confidence = self.ocr_result
                if found:
                    self._update_detected_areas(boxes)
            
            processed_frame = self._draw_boxes(frame, word_count, boxes,
                                            getattr(self, 'last_ocr_time', None),
                                            len(motion_boxes))
            
            cv2.imshow(window_name, processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.recording = False
                break
            
            if self.skip_frames > 0:
                time.sleep(1/(self.fps * 2))
            else:
                time.sleep(1/self.fps)
        
        cap.release()
        cv2.destroyAllWindows()
        
        for thread in self.processing_queue:
            thread.join()

    def _process_webcam_integrated(self):
        if not self.cap:
            self.out.error("OCR", "camera not ready")
            return
            
        width = int(1920 * self.scale_factor)
        height = int(1080 * self.scale_factor)
        
        self.out.success("OCR", "starting video loop")
        prev_gray = None
        frame_skip_count = 0
        
        while self.recording:
            ret, frame = self.cap.read()
            
            if not ret:
                self.out.warn("OCR", "bad frame")
                break
            
            frame = cv2.resize(frame, (width, height))
            self.frame_count += 1
            
            if self.frame_count % 60 == 0:
                self.out.log("OCR", f"processed {self.frame_count} frames")
            
            prev_gray, frame, motion_boxes = self._draw_motion(frame, prev_gray)
            
            if self.frame_count % self.ocr_interval == 0 and not self.ocr_pending:
                self._process_frame_parallel(frame, motion_boxes)
            elif self.ocr_pending:
                frame_skip_count += 1
                if frame_skip_count % 20 == 0:
                    self.out.warn("OCR", f"ocr pending, skipped {frame_skip_count} frames")
            
            self._cleanup_threads()
            
            with self.lock:
                found, word_count, boxes, confidence = self.ocr_result
                if found:
                    self._update_detected_areas(boxes)
            
            processed_frame = self._draw_boxes(frame, word_count, boxes,
                                            getattr(self, 'last_ocr_time', None),
                                            len(motion_boxes))
            
            cv2.imshow("Webcam OCR", processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.out.info("OCR", "quitting...")
                self.recording = False
                break
            
            if self.skip_frames > 0:
                time.sleep(1/(self.fps * 2))
            else:
                time.sleep(1/self.fps)
        
        self.cap.release()
        cv2.destroyAllWindows()
        self.out.warn("OCR", "stopped")
        
        for thread in self.processing_queue:
            thread.join()


def main():
    print("Select mode:")
    print("1: Screen OCR")
    print("2: Webcam OCR")
    mode = input("Enter 1 or 2: ").strip()
    detector = TextDetector(target_word="chicken", fps=30)
    if mode == '1':
        print("Starting screen text detection... Press 'q' to quit.")
        detector.start_screen_recording()
    elif mode == '2':
        print("Starting webcam text detection... Press 'q' to quit.")
        detector.start_webcam_recording()
    else:
        print("Invalid input. Exiting.")
        return
    while detector.recording:
        time.sleep(0.1)

if __name__ == "__main__":
    main()
    
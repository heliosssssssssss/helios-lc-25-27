import numpy as np
import cv2
import pyautogui
import time
from threading import Thread, Lock
import easyocr
import re
import torch

class TextDetector:
    def __init__(self, target_word="chicken", fps=30):
        self.fps = fps
        self.recording = False
        self.frame = None
        self.target_word = target_word.lower()
        self.ocr_result = (False, 0, [], 0.0)
        self.frame_count = 0
        self.ocr_interval = 1  # Real-time OCR on every frame
        self.scale_factor = 0.7
        self.lock = Lock()
        self.detected_areas = []
        self.area_persistence = 0.3
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
        # Add new motion vector settings
        self.motion_vector_interval = 3  # Calculate vectors every 3 frames
        self.show_motion_vectors = True  # Toggle for motion vector visualization
        self.motion_grid_step = 40  # Increased grid step for fewer vectors
        self.min_motion_magnitude = 8  # Increased minimum magnitude threshold
        # Add brightness control parameters
        self.brightness_threshold = 245  # Require extremely bright light for detection
        self.exposure_compensation = 1.0  # Current exposure compensation
        self.max_exposure_compensation = 0.2  # More aggressive exposure reduction
        self.min_exposure_compensation = 1.0  # Minimum exposure reduction
        self.exposure_adjustment_speed = 0.2  # Faster adjustment
        self.brightness_history = []  # Store recent brightness values
        self.brightness_history_size = 5  # Reduced history for faster response
        
        # Initialize fast reader with minimal settings
        if torch.cuda.is_available():
            print("[INFO] CUDA GPU detected. Using GPU for EasyOCR.")
            self.fast_reader = easyocr.Reader(
                ['en'], 
                gpu=True,
                model_storage_directory='./fast_ocr',
                download_enabled=True,
                quantize=True,
                verbose=False
            )
            self.reader = self.fast_reader  # Use same reader for both modes
        else:
            print("[WARNING] No CUDA GPU detected! Performance may be slower.")
            self.fast_reader = easyocr.Reader(['en'], gpu=True, verbose=False)
            self.reader = self.fast_reader

    def start_screen_recording(self):
        self.recording = True
        Thread(target=self._process_screen).start()

    def start_webcam_recording(self):
        self.recording = True
        Thread(target=self._process_webcam).start()

    def stop_recording(self):
        self.recording = False

    def _calculate_motion_vectors(self, prev_gray, current_gray, min_magnitude=8):
        """Calculate motion vectors between two frames"""
        if prev_gray is None or current_gray is None:
            return []
            
        # Resize images for faster processing
        scale = 0.5
        h, w = prev_gray.shape
        small_h, small_w = int(h * scale), int(w * scale)
        prev_small = cv2.resize(prev_gray, (small_w, small_h))
        curr_small = cv2.resize(current_gray, (small_w, small_h))
        
        # Calculate optical flow with optimized parameters
        flow = cv2.calcOpticalFlowFarneback(
            prev_small, curr_small, 
            None,
            0.5,    # Pyramid scale
            2,      # Reduced pyramid levels
            10,     # Reduced window size
            2,      # Reduced iterations
            5,      # Poly neighborhood
            1.2,    # Poly sigma
            0
        )
        
        # Sample points on a sparse grid
        vectors = []
        for y in range(0, small_h, self.motion_grid_step):
            for x in range(0, small_w, self.motion_grid_step):
                # Get flow at this point
                fx, fy = flow[y, x]
                magnitude = np.sqrt(fx*fx + fy*fy)
                
                # Only keep significant movements
                if magnitude > min_magnitude:
                    # Scale coordinates back to original size
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
            # Only calculate motion vectors every few frames
            if self.show_motion_vectors and self.frame_count % self.motion_vector_interval == 0:
                motion_vectors = self._calculate_motion_vectors(prev_gray, gray, self.min_motion_magnitude)
                
                # Draw motion vectors
                for vec in motion_vectors:
                    start = vec['start']
                    end = vec['end']
                    magnitude = vec['magnitude']
                    
                    # Color based on magnitude
                    color = (0, 0, 255)  # Default to red
                    if magnitude < 10:
                        color = (0, 255, 0)  # Green for small movements
                    elif magnitude < 20:
                        color = (0, 255, 255)  # Yellow for medium movements
                    
                    # Draw arrow with reduced thickness
                    cv2.arrowedLine(frame, start, end, color, 1, tipLength=0.2)
            
            # Original motion detection code
            frame_delta = cv2.absdiff(prev_gray, gray)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            grouped_boxes = []
            for c in contours:
                if cv2.contourArea(c) < min_area:
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
                    # Draw red rectangle for motion
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                
                # Draw semi-transparent orange skeleton lines
                if len(merged_boxes) > 1:
                    centers = [(x + w//2, y + h//2) for (x, y, w, h) in merged_boxes]
                    centers.sort(key=lambda x: x[0])
                    
                    # Create overlay for transparent lines
                    overlay = frame.copy()
                    for i in range(len(centers) - 1):
                        pt1 = centers[i]
                        pt2 = centers[i + 1]
                        cv2.line(overlay, pt1, pt2, (0, 165, 255), 2)
                        cv2.circle(overlay, pt1, 4, (0, 165, 255), -1)
                        cv2.circle(overlay, pt2, 4, (0, 165, 255), -1)
                    # Apply transparency
                    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        return gray, frame, motion_boxes

    def _update_detected_areas(self, boxes):
        now = time.time()
        
        # Clear all boxes if we haven't had a detection for a while
        if not boxes:
            time_since_last_detection = now - self.last_detection_time
            if time_since_last_detection > self.area_persistence:
                print(f"[DEBUG] No detection for {time_since_last_detection:.2f}s, clearing all boxes")
                self.detected_areas = []
                return
        
        # Only add new blue boxes if the word is detected (boxes is not empty)
        if boxes:
            self.last_detection_time = now  # Update last detection time
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
        
        # Remove old detections more aggressively
        self.detected_areas = [(box, timestamp, center) for box, timestamp, center in self.detected_areas 
                             if (now - timestamp < self.area_persistence and 
                                 now - self.last_detection_time < self.area_persistence)]
        
        # Clean up trail points
        active_centers = set(tuple(center) for _, _, center in self.detected_areas)
        self.trail_points = [(point, timestamp) for point, timestamp in self.trail_points 
                           if now - timestamp < self.trail_persistence and tuple(point) in active_centers]
        
        # Only merge if we still have boxes
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
        """Detect bright areas and gently reduce exposure only in those regions, with a gentle sharpening filter for OCR and debug info"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2]
        _, bright_mask = cv2.threshold(v_channel, self.brightness_threshold, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        adjusted = frame.copy()
        exposure_values = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                region_brightness = np.mean(v_channel[y:y+h, x:x+w])
                # Gentle exposure reduction: alpha between 0.6 and 0.8
                compensation = max(0.6, min(0.8, 1.0 - (region_brightness - self.brightness_threshold) / 255.0))
                exposure_values.append(compensation)
                roi = adjusted[y:y+h, x:x+w]
                roi = cv2.convertScaleAbs(roi, alpha=compensation, beta=0)
                # Gentle sharpening filter
                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                roi = cv2.filter2D(roi, -1, kernel)
                adjusted[y:y+h, x:x+w] = roi
        avg_exposure = np.mean(exposure_values) if exposure_values else 1.0
        avg_brightness = np.mean(v_channel)
        cv2.putText(adjusted, f"Brightness: {avg_brightness:.1f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(adjusted, f"Average Exposure Debug: {avg_exposure:.2f}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        return adjusted

    def _preprocess_roi(self, roi):
        # First adjust brightness if needed
        roi = self._adjust_brightness(roi)
        
        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # Sharpen
        kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        sharp = cv2.filter2D(gray, -1, kernel)
        # Increase contrast
        contrast = cv2.convertScaleAbs(sharp, alpha=1.5, beta=0)
        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        # Convert back to BGR for EasyOCR
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    def _preprocess_roi_fast(self, roi):
        """Ultra-fast preprocessing with brightness adjustment and mild deblurring for moving/bright regions"""
        if roi.size == 0:
            return None
        # Adjust brightness first
        roi = self._adjust_brightness(roi)
        # Expand ROI by 20% for moving/bright regions
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
        # Resize to smaller size for faster processing
        h, w = roi.shape[:2]
        new_h = min(h, 100)  # Cap height at 100 pixels
        scale = new_h / h
        new_w = int(w * scale)
        roi = cv2.resize(roi, (new_w, new_h))
        # Fast grayscale conversion and threshold
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        # Mild unsharp mask (deblurring)
        blur = cv2.GaussianBlur(thresh, (3, 3), 0)
        sharp = cv2.addWeighted(thresh, 1.5, blur, -0.5, 0)
        return cv2.cvtColor(sharp, cv2.COLOR_GRAY2BGR)

    def _predict_next_box(self, current_time):
        """Predict box location based on velocity"""
        if self.last_valid_box is None or self.box_velocity is None:
            return None
            
        time_diff = current_time - self.last_box_time
        if time_diff > 0.5:  # Don't predict if too much time has passed
            return None
            
        # Predict new position based on velocity
        predicted_box = []
        for point in self.last_valid_box:
            new_x = point[0] + self.box_velocity[0] * time_diff
            new_y = point[1] + self.box_velocity[1] * time_diff
            predicted_box.append((int(new_x), int(new_y)))
            
        return predicted_box

    def _update_box_velocity(self, new_box):
        """Update velocity based on box movement"""
        if self.last_valid_box is None:
            self.last_valid_box = new_box
            self.last_box_time = time.time()
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_box_time
        if time_diff > 0:
            # Calculate center points
            old_center = np.mean(self.last_valid_box, axis=0)
            new_center = np.mean(new_box, axis=0)
            
            # Calculate velocity (pixels per second)
            velocity_x = (new_center[0] - old_center[0]) / time_diff
            velocity_y = (new_center[1] - old_center[1]) / time_diff
            
            # Update velocity with smoothing
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
        pattern = re.compile(r'chicken', re.IGNORECASE)
        boxes = []
        max_confidence = 0.0  # Track highest confidence
        # Predict next location
        predicted_box = self._predict_next_box(start_time)
        if predicted_box is not None:
            # Create ROI around predicted location
            x_coords = [p[0] for p in predicted_box]
            y_coords = [p[1] for p in predicted_box]
            x1, x2 = min(x_coords), max(x_coords)
            y1, y2 = min(y_coords), max(y_coords)
            # Add padding and expand ROI by 20%
            pad = 20
            x1 = max(0, x1 - pad)
            y1 = max(0, y1 - pad)
            x2 = min(frame.shape[1], x2 + pad)
            y2 = min(frame.shape[0], y2 + pad)
            # Expand ROI
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
                    for (bbox, text, conf) in results:
                        if pattern.search(text):
                            found = True
                            word_count += 1
                            max_confidence = max(max_confidence, conf)  # Update max confidence
                            bbox_global = [(int(x1 + bx), int(y1 + by)) for (bx, by) in bbox]
                            boxes.append(bbox_global)
                            self._update_box_velocity(bbox_global)
                            break
        # If not found in predicted location, check motion boxes
        if not found:
            for (x, y, w, h) in motion_boxes:
                # Expand ROI by 20%
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
                    for (bbox, text, conf) in results:
                        if pattern.search(text):
                            found = True
                            word_count += 1
                            max_confidence = max(max_confidence, conf)  # Update max confidence
                            bbox_global = [(int(x1 + bx), int(y1 + by)) for (bx, by) in bbox]
                            boxes.append(bbox_global)
                            self._update_box_velocity(bbox_global)
                            break
                if found:
                    break
        elapsed = time.time() - start_time
        print(f"[EasyOCR] Frame OCR time: {elapsed:.3f} seconds")
        self.last_ocr_time = elapsed
        with self.lock:
            self.ocr_result = (found, word_count, boxes, max_confidence)
            self.ocr_pending = False

    def _detect_bright_regions(self, frame):
        """Detect regions with high brightness"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2]
        
        # Create binary mask for bright regions with lower threshold
        _, bright_mask = cv2.threshold(v_channel, self.brightness_threshold, 255, cv2.THRESH_BINARY)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((5,5), np.uint8)
        bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)
        bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours of bright regions
        contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and merge bright regions
        bright_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                # Expand the region slightly to ensure we capture the full bright area
                x = max(0, x - 5)
                y = max(0, y - 5)
                w = min(frame.shape[1] - x, w + 10)
                h = min(frame.shape[0] - y, h + 10)
                bright_regions.append((x, y, w, h))
        
        # Merge overlapping regions
        if bright_regions:
            merged_regions = []
            current_region = list(bright_regions[0])
            
            for region in bright_regions[1:]:
                x, y, w, h = region
                if (abs(current_region[0] - x) < 50 and abs(current_region[1] - y) < 50):
                    # Merge regions
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
        # Draw predicted box if available
        current_time = time.time()
        predicted_box = self._predict_next_box(current_time)
        if predicted_box is not None:
            pts_np = np.array(predicted_box, dtype=np.int32)
            cv2.polylines(frame, [pts_np], isClosed=True, color=(255,165,0), thickness=1)  # Orange outline
        
        # Draw skeleton lines between motion boxes if they exist
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
        
        # Draw yellow line between last two blue box centers ever
        if len(self.prev_blue_centers) >= 2:
            pt1 = self.prev_blue_centers[-2]
            pt2 = self.prev_blue_centers[-1]
            cv2.line(frame, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])), (0, 255, 255), 4)
        
        # Draw blue boxes for tracked areas
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
        
        # Draw green boxes for current detections
        for pts in boxes:
            pts_np = np.array(pts, dtype=np.int32)
            cv2.polylines(frame, [pts_np], isClosed=True, color=(0,255,0), thickness=4)
            overlay = frame.copy()
            cv2.fillPoly(overlay, [pts_np], (0,255,0))
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        # Draw purple outline boxes for bright regions (drawn last)
        bright_regions = self._detect_bright_regions(frame)
        for (x, y, w, h) in bright_regions:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)  # Purple outline

        if word_count > 0:
            cv2.putText(frame, f"Found {word_count} instances of '{self.target_word}'", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, f"Found no instances of '{self.target_word}'", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Active tracking regions: {len(self.detected_areas)}", 
                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        if ocr_time is not None:
            cv2.putText(frame, f"OCR time: {ocr_time:.3f}s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        if motion_box_count is not None:
            cv2.putText(frame, f"Active motion boxes: {motion_box_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 128, 255), 2)
        
        # Add confidence level in right corner
        with self.lock:
            _, _, _, confidence = self.ocr_result
            if confidence > 0:
                # Calculate position in right corner
                text = f"Confidence: {confidence:.2%}"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                x = frame.shape[1] - text_size[0] - 10  # 10 pixels padding from right edge
                y = 30  # 30 pixels from top
                cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        return frame

    def _process_frame_parallel(self, frame, motion_boxes):
        """Process a frame in parallel if queue isn't full"""
        if len(self.processing_queue) < self.max_queue_size and not self.ocr_pending:
            self.ocr_pending = True  # Set flag before starting thread
            thread = Thread(target=self._ocr_worker, args=(frame.copy(), motion_boxes))
            thread.start()
            self.processing_queue.append(thread)
            self.ocr_thread = thread
        else:
            # If queue is full or OCR is pending, try to remove completed threads
            self._cleanup_threads()
            if len(self.processing_queue) < self.max_queue_size and not self.ocr_pending:
                self.ocr_pending = True  # Set flag before starting thread
                thread = Thread(target=self._ocr_worker, args=(frame.copy(), motion_boxes))
                thread.start()
                self.processing_queue.append(thread)
                self.ocr_thread = thread

    def _cleanup_threads(self):
        """Clean up completed processing threads"""
        self.processing_queue = [t for t in self.processing_queue if t.is_alive()]

    def _process_screen(self):
        prev_gray = None
        while self.recording:
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Scale down the frame
            height, width = frame.shape[:2]
            new_height = int(height * self.scale_factor)
            new_width = int(width * self.scale_factor)
            frame = cv2.resize(frame, (new_width, new_height))
            
            self.frame_count += 1
            prev_gray, frame, motion_boxes = self._draw_motion(frame, prev_gray)
            
            # Process frame in parallel if it's time
            if self.frame_count % self.ocr_interval == 0 and not self.ocr_pending:
                self._process_frame_parallel(frame, motion_boxes)
            
            # Clean up completed threads
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
            
            # Adaptive frame rate control
            if self.skip_frames > 0:
                time.sleep(1/(self.fps * 2))  # Sleep less if we're skipping frames
            else:
                time.sleep(1/self.fps)
        
        # Clean up
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
    
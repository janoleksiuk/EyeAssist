"""Calibration system for eye tracking."""

import cv2
import time
import winsound
from typing import Dict, Any
from config.config import *


class CalibrationData:
    """Stores calibration data and thresholds."""
    
    def __init__(self):
        self.lu_side = 0.0  # left-up side ratio
        self.ru_side = 0.0  # right-up side ratio
        self.ld_side = 0.0  # left-down side ratio
        self.rd_side = 0.0  # right-down side ratio
        self.tb = 0.0       # top-bottom ratio
        self.mouth = 0.0    # mouth ratio
    
    def save_to_file(self, filename: str = CALIBRATION_FILE):
        """Save calibration data to file."""
        with open(filename, "w") as f:
            f.write(f"{self.lu_side},{self.ru_side},{self.ld_side},{self.rd_side},{self.tb},{self.mouth}")
    
    @classmethod
    def load_from_file(cls, filename: str = CALIBRATION_FILE) -> 'CalibrationData':
        """Load calibration data from file."""
        data = cls()
        with open(filename, 'r') as f:
            line = f.readline().strip()
            params = line.split(",")
            data.lu_side = float(params[0])
            data.ru_side = float(params[1])
            data.ld_side = float(params[2])
            data.rd_side = float(params[3])
            data.tb = float(params[4])
            data.mouth = float(params[5])
        return data


class CalibrationSystem:
    """Manages the calibration process."""
    
    def __init__(self, eye_tracker, face_detector):
        self.eye_tracker = eye_tracker
        self.face_detector = face_detector
        self.images = self._load_images()
        self.reset_calibration()
    
    def _load_images(self) -> Dict[str, Any]:
        """Load all calibration images."""
        images = {}
        for key, path in CALIBRATION_IMAGES.items():
            images[key] = cv2.imread(path, 1)
        return images
    
    def reset_calibration(self):
        """Reset calibration state."""
        self.flag = 0
        self.accumulated_side = 0.0
        self.accumulated_top = 0.0
        self.accumulated_mouth = 0.0
        self.count = 0
        self.timer = 0.0
        self.data = CalibrationData()
        self.stage_data = {}
    
    def display_fullscreen(self, window_name: str, image):
        """Display image in fullscreen mode."""
        if image is not None:
            cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow(window_name, image)
    
    def process_frame(self, frame, gray):
        """Process a single frame during calibration."""
        faces = self.face_detector.detect_faces(frame)
        
        for face in faces:
            landmarks = self.face_detector.get_landmarks(gray, face)
            if landmarks is None:
                continue
            
            # Calculate ratios
            l_blink = self.eye_tracker.get_blinking_ratio(LEFT_EYE_POINTS, landmarks)
            r_blink = self.eye_tracker.get_blinking_ratio(RIGHT_EYE_POINTS, landmarks)
            tb_ratio = (l_blink[1] + r_blink[1]) / 2
            
            left_gaze = self.eye_tracker.get_gaze_ratio(LEFT_EYE_POINTS, landmarks, frame, gray)
            right_gaze = self.eye_tracker.get_gaze_ratio(RIGHT_EYE_POINTS, landmarks, frame, gray)
            side_ratio = (left_gaze + right_gaze) / 2
            
            mouth_ratio = self.eye_tracker.get_mouth_ratio(MOUTH_POINTS, landmarks)
            
            # Accumulate data for active calibration stages
            if self.flag in [2, 4, 6, 8]:  # Position calibration stages
                self.accumulated_side += side_ratio
                self.accumulated_top += tb_ratio
                self.count += 1
                
                stage_name = {2: 'lu', 4: 'ru', 6: 'rd', 8: 'ld'}[self.flag]
                self.stage_data[f'{stage_name}_side'] = self.accumulated_side / self.count
                self.stage_data[f'tb_{self.flag//2}'] = self.accumulated_top / self.count
                
            elif self.flag == 10:  # Mouth calibration
                self.accumulated_mouth += mouth_ratio
                self.count += 1
                self.data.mouth = self.accumulated_mouth / self.count
    
    def update_display(self):
        """Update the calibration display based on current flag."""
        display_map = {
            0: 'centerline',
            1: 'pre_1',
            2: 'stage_1',
            3: 'pre_2',
            4: 'stage_2',
            5: 'pre_3',
            6: 'stage_3',
            7: 'pre_4',
            8: 'stage_4',
            9: 'pre_5',
            10: 'stage_5'
        }
        
        if self.flag in display_map:
            self.display_fullscreen("Calib", self.images[display_map[self.flag]])
    
    def handle_timing(self):
        """Handle timing for automatic stage progression."""
        if self.flag % 2 == 0 and self.flag != 0:  # Active calibration stages
            if time.time() - self.timer > CALIBRATION_DURATION:
                if self.flag == 10:
                    winsound.Beep(CALIBRATION_COMPLETE_FREQUENCY, CALIBRATION_COMPLETE_DURATION)
                self._advance_stage()
                cv2.destroyWindow("Calib")
    
    def handle_keypress(self, key: int):
        """Handle ESC key press to advance stages."""
        if key == 27 and (self.flag % 2 == 1 or self.flag == 0):  # ESC key on preparation stages
            self._advance_stage()
            cv2.destroyWindow("Calib")
            self.timer = time.time()
    
    def _advance_stage(self):
        """Advance to the next calibration stage."""
        self.flag += 1
        self.accumulated_side = 0.0
        self.accumulated_top = 0.0
        self.accumulated_mouth = 0.0
        self.count = 0
    
    def is_complete(self) -> bool:
        """Check if calibration is complete."""
        return self.flag >= 11
    
    def finalize_calibration(self):
        """Calculate final calibration values and save to file."""
        self.data.lu_side = self.stage_data.get('lu_side', 0.0)
        self.data.ru_side = self.stage_data.get('ru_side', 0.0)
        self.data.ld_side = self.stage_data.get('ld_side', 0.0)
        self.data.rd_side = self.stage_data.get('rd_side', 0.0)
        
        # Calculate average TB ratio
        tb_values = [self.stage_data.get(f'tb_{i}', 0.0) for i in range(1, 5)]
        self.data.tb = sum(tb_values) / len(tb_values) if tb_values else 0.0
        
        self.data.save_to_file()
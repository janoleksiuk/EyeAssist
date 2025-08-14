"""
Eye Detection Module
Handles face detection, landmark detection, and eye/gaze ratio calculations
"""

import cv2
import numpy as np
import dlib
from math import hypot
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class BlinkRatio:
    """Data class for blink ratio information"""
    ratio: float
    tb_ratio: float


@dataclass 
class GazeRatio:
    """Data class for gaze ratio information"""
    side_ratio: float
    left_eye_ratio: float
    right_eye_ratio: float


class EyeDetector:
    """Handles eye detection and gaze tracking"""
    
    # Eye landmark indices
    LEFT_EYE_POINTS = [36, 37, 38, 39, 40, 41]
    RIGHT_EYE_POINTS = [42, 43, 44, 45, 46, 47]
    MOUTH_POINTS = [62, 66, 60, 64]
    
    def __init__(self, model_path: str):
        """Initialize the eye detector with dlib models"""
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(model_path)
    
    def detect_faces(self, gray_frame: np.ndarray) -> List:
        """Detect faces in the grayscale frame"""
        return self.detector(gray_frame)
    
    def get_landmarks(self, gray_frame: np.ndarray, face_rect) -> dlib.full_object_detection:
        """Get facial landmarks for a detected face"""
        return self.predictor(gray_frame, face_rect)
    
    @staticmethod
    def midpoint(p1, p2) -> Tuple[int, int]:
        """Calculate midpoint between two dlib points"""
        return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)
    
    def get_eye_blink_ratio(self, eye_points: List[int], landmarks) -> BlinkRatio:
        """Calculate blink ratio for a single eye"""
        left_point = (landmarks.part(eye_points[0]).x, landmarks.part(eye_points[0]).y)
        right_point = (landmarks.part(eye_points[3]).x, landmarks.part(eye_points[3]).y)
        center_top = self.midpoint(landmarks.part(eye_points[1]), landmarks.part(eye_points[2]))
        center_bottom = self.midpoint(landmarks.part(eye_points[5]), landmarks.part(eye_points[4]))
        center = self.midpoint(landmarks.part(eye_points[0]), landmarks.part(eye_points[3]))
        
        # Calculate distances
        hor_line_length = hypot(left_point[0] - right_point[0], left_point[1] - right_point[1])
        ver_line_length = hypot(center_top[0] - center_bottom[0], center_top[1] - center_bottom[1])
        up_ver_line_length = hypot(center_top[0] - center[0], center_top[1] - center[1])
        bot_ver_line_length = hypot(center[0] - center_bottom[0], center[1] - center_bottom[1])
        
        # Calculate ratios
        blink_ratio = hor_line_length / ver_line_length if ver_line_length != 0 else 0
        tb_ratio = up_ver_line_length / bot_ver_line_length if bot_ver_line_length != 0 else 1.5
        
        return BlinkRatio(blink_ratio, tb_ratio)
    
    def get_blink_ratio(self, landmarks) -> float:
        """Get average blink ratio from both eyes"""
        left_blink = self.get_eye_blink_ratio(self.LEFT_EYE_POINTS, landmarks)
        right_blink = self.get_eye_blink_ratio(self.RIGHT_EYE_POINTS, landmarks)
        return (left_blink.ratio + right_blink.ratio) / 2
    
    def get_tb_ratio(self, landmarks) -> float:
        """Get average top-bottom ratio from both eyes"""
        left_blink = self.get_eye_blink_ratio(self.LEFT_EYE_POINTS, landmarks)
        right_blink = self.get_eye_blink_ratio(self.RIGHT_EYE_POINTS, landmarks)
        return (left_blink.tb_ratio + right_blink.tb_ratio) / 2
    
    def get_mouth_ratio(self, landmarks) -> float:
        """Calculate mouth opening ratio"""
        mouth_points = self.MOUTH_POINTS
        up_mouth = landmarks.part(mouth_points[0])
        bot_mouth = landmarks.part(mouth_points[1])
        left_mouth = landmarks.part(mouth_points[2])
        right_mouth = landmarks.part(mouth_points[3])
        
        mouth_hor_line = hypot(up_mouth.x - bot_mouth.x, up_mouth.y - bot_mouth.y)
        mouth_ver_line = hypot(left_mouth.x - right_mouth.x, left_mouth.y - right_mouth.y)
        
        return mouth_hor_line / mouth_ver_line if mouth_ver_line != 0 else 0
    
    def get_single_eye_gaze_ratio(self, eye_points: List[int], landmarks, frame: np.ndarray, gray: np.ndarray) -> float:
        """Calculate gaze ratio for a single eye"""
        # Create eye region polygon
        eye_region = np.array([
            (landmarks.part(eye_points[i]).x, landmarks.part(eye_points[i]).y) 
            for i in range(6)
        ], np.int32)
        
        height, width, _ = frame.shape
        mask = np.zeros((height, width), np.uint8)
        
        # Create mask for eye region
        cv2.polylines(mask, [eye_region], True, 255, 2)
        cv2.fillPoly(mask, [eye_region], 255)
        eye = cv2.bitwise_and(gray, gray, mask=mask)
        
        # Get bounding box of eye
        min_x = np.min(eye_region[:, 0])
        max_x = np.max(eye_region[:, 0])
        min_y = np.min(eye_region[:, 1])
        max_y = np.max(eye_region[:, 1])
        
        # Extract eye region with padding
        gray_eye = eye[min_y:max_y, min_x + 4:max_x - 4]
        
        if gray_eye.size == 0:
            return 1.0  # Default ratio if eye region is invalid
        
        # Apply blur and threshold
        blurred = cv2.GaussianBlur(gray_eye, (5, 5), 0)
        _, threshold_eye = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        height, width = threshold_eye.shape
        
        # Split eye into left and right halves
        left_side_threshold = threshold_eye[0:height, 0:int(width/2)]
        left_side_white = cv2.countNonZero(left_side_threshold)
        
        right_side_threshold = threshold_eye[0:height, int(width/2):width]
        right_side_white = cv2.countNonZero(right_side_threshold)
        
        # Calculate gaze ratio
        if right_side_white == 0:
            return 2.0
        elif left_side_white == 0:
            return 0.5
        else:
            return left_side_white / right_side_white
    
    def get_gaze_ratio(self, landmarks, frame: np.ndarray, gray: np.ndarray) -> float:
        """Get average gaze ratio from both eyes"""
        left_ratio = self.get_single_eye_gaze_ratio(self.LEFT_EYE_POINTS, landmarks, frame, gray)
        right_ratio = self.get_single_eye_gaze_ratio(self.RIGHT_EYE_POINTS, landmarks, frame, gray)
        return (left_ratio + right_ratio) / 2
    
    def get_detailed_gaze_info(self, landmarks, frame: np.ndarray, gray: np.ndarray) -> GazeRatio:
        """Get detailed gaze information for both eyes"""
        left_ratio = self.get_single_eye_gaze_ratio(self.LEFT_EYE_POINTS, landmarks, frame, gray)
        right_ratio = self.get_single_eye_gaze_ratio(self.RIGHT_EYE_POINTS, landmarks, frame, gray)
        side_ratio = (left_ratio + right_ratio) / 2
        
        return GazeRatio(side_ratio, left_ratio, right_ratio)
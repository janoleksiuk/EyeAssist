"""Core eye tracking functionality."""

import cv2
import numpy as np
from typing import Tuple, List
from math import hypot
from utils.geometry_utils import midpoint, calculate_distance


class EyeTracker:
    """Handles eye tracking calculations and gaze detection."""
    
    def get_tb_ratio(self, eye_points: List[int], landmarks) -> float:
        """Calculate top-bottom ratio for eye positioning."""
        center_top = midpoint(landmarks.part(eye_points[1]), landmarks.part(eye_points[2]))
        center_bottom = midpoint(landmarks.part(eye_points[5]), landmarks.part(eye_points[4]))
        center = midpoint(landmarks.part(eye_points[0]), landmarks.part(eye_points[3]))

        up_length = calculate_distance(center_top, center)
        bot_length = calculate_distance(center, center_bottom)

        if bot_length == 0:
            return 1.5
        return up_length / bot_length
    
    def get_blinking_ratio(self, eye_points: List[int], landmarks) -> Tuple[float, float]:
        """Calculate blinking ratio and top-bottom ratio."""
        left_point = (landmarks.part(eye_points[0]).x, landmarks.part(eye_points[0]).y)
        right_point = (landmarks.part(eye_points[3]).x, landmarks.part(eye_points[3]).y)
        center_top = midpoint(landmarks.part(eye_points[1]), landmarks.part(eye_points[2]))
        center_bottom = midpoint(landmarks.part(eye_points[5]), landmarks.part(eye_points[4]))
        center = midpoint(landmarks.part(eye_points[0]), landmarks.part(eye_points[3]))
        
        hor_length = calculate_distance(left_point, right_point)
        ver_length = calculate_distance(center_top, center_bottom)
        up_length = calculate_distance(center_top, center)
        bot_length = calculate_distance(center, center_bottom)
        
        blink_ratio = hor_length / ver_length if ver_length != 0 else 0
        tb_ratio = 5 if bot_length == 0 else up_length / bot_length
        
        return blink_ratio, tb_ratio
    
    def get_mouth_ratio(self, mouth_points: List[int], landmarks) -> float:
        """Calculate mouth opening ratio."""
        up_mouth = landmarks.part(mouth_points[0])
        bot_mouth = landmarks.part(mouth_points[1])
        left_mouth = landmarks.part(mouth_points[2])
        right_mouth = landmarks.part(mouth_points[3])

        mouth_hor = hypot(up_mouth.x - bot_mouth.x, up_mouth.y - bot_mouth.y)
        mouth_ver = hypot(left_mouth.x - right_mouth.x, left_mouth.y - right_mouth.y)

        return mouth_hor / mouth_ver if mouth_ver != 0 else 0
    
    def get_gaze_ratio(self, eye_points: List[int], landmarks, frame: np.ndarray, gray: np.ndarray) -> float:
        """Calculate gaze ratio for horizontal eye movement detection."""
        eye_region = np.array([
            (landmarks.part(point).x, landmarks.part(point).y) for point in eye_points
        ], np.int32)
        
        height, width, _ = frame.shape
        mask = np.zeros((height, width), np.uint8)

        cv2.polylines(mask, [eye_region], True, 255, 2)
        cv2.fillPoly(mask, [eye_region], 255)
        eye = cv2.bitwise_and(gray, gray, mask=mask)

        min_x, max_x = np.min(eye_region[:, 0]), np.max(eye_region[:, 0])
        min_y, max_y = np.min(eye_region[:, 1]), np.max(eye_region[:, 1])

        gray_eye = eye[min_y:max_y, min_x + 4:max_x - 4]

        blurred = cv2.GaussianBlur(gray_eye, (5, 5), 0)
        _, threshold_eye = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        if threshold_eye.size == 0:
            return 1.0
            
        height, width = threshold_eye.shape
        left_threshold = threshold_eye[0:height, 0:int(width / 2)]
        left_white = cv2.countNonZero(left_threshold)

        right_threshold = threshold_eye[0:height, int(width / 2):width]
        right_white = cv2.countNonZero(right_threshold)

        if right_white == 0:
            return 2.0
        return left_white / right_white

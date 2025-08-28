"""Face detection and landmark extraction."""

import cv2
import dlib
import numpy as np
from typing import Optional, List, Tuple
from config.config import SHAPE_PREDICTOR_PATH


class FaceDetector:
    """Handles face detection and facial landmark prediction."""
    
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(SHAPE_PREDICTOR_PATH)
    
    def detect_faces(self, frame: np.ndarray) -> List:
        """Detect faces in the given frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.detector(gray)
    
    def get_landmarks(self, gray_frame: np.ndarray, face) -> Optional[dlib.full_object_detection]:
        """Get facial landmarks for a detected face."""
        return self.predictor(gray_frame, face)
    
    def is_face_detected(self, faces) -> bool:
        """Check if any faces were detected."""
        return str(faces) != "rectangles[]"

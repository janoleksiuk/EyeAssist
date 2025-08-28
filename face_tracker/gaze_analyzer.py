"""Gaze analysis and position detection."""

from typing import Tuple
from face_tracker.calibration import CalibrationData
from config.config import MOUTH_THRESHOLD_MULTIPLIER


class GazeAnalyzer:
    """Analyzes gaze direction and detects positions."""
    
    def __init__(self, calibration_data: CalibrationData):
        self.calib = calibration_data
        self.mouth_threshold = calibration_data.mouth * MOUTH_THRESHOLD_MULTIPLIER
    
    def analyze_position(self, side_ratio: float, tb_ratio: float) -> Tuple[bool, bool, bool, bool, bool]:
        """
        Analyze gaze position and return flags.
        Returns: (center_flag, right_flag, left_flag, top_flag, bot_flag)
        """
        center_flag = right_flag = left_flag = top_flag = bot_flag = False
        
        if tb_ratio > self.calib.tb:
            top_flag = True
            if side_ratio < self.calib.ru_side:
                right_flag = True
            elif side_ratio > self.calib.lu_side:
                left_flag = True
            else:
                center_flag = True
        else:
            bot_flag = True
            if side_ratio < self.calib.rd_side:
                right_flag = True
            elif side_ratio > self.calib.ld_side:
                left_flag = True
            else:
                center_flag = True
        
        return center_flag, right_flag, left_flag, top_flag, bot_flag
    
    def is_mouth_open(self, mouth_ratio: float) -> bool:
        """Check if mouth is open based on calibrated threshold."""
        return mouth_ratio > self.mouth_threshold

"""Main eye tracking application."""

import cv2
import time
from typing import List
from face_tracker.face_detector import FaceDetector
from face_tracker.eye_tracker import EyeTracker
from face_tracker.gaze_analyzer import GazeAnalyzer
from face_tracker.calibration import CalibrationData
from utils.data_processing import moving_average, rearrange_circular_buffer
from config.config import LEFT_EYE_POINTS, RIGHT_EYE_POINTS, MOUTH_POINTS, MOVING_AVERAGE_WINDOW
from memory_sharing import MemoryShare


class EyeTrackingSystem:
    """Main eye tracking system."""
    
    def __init__(self):
        self.face_detector = FaceDetector()
        self.eye_tracker = EyeTracker()
        self.calibration_data = CalibrationData.load_from_file()
        self.gaze_analyzer = GazeAnalyzer(self.calibration_data)

        # Initialize shared memory
        self.memory = MemoryShare()
        
        # Initialize filtering buffers
        self.side_buffer: List[float] = [0.0] * MOVING_AVERAGE_WINDOW
        self.tb_buffer: List[float] = [0.0] * MOVING_AVERAGE_WINDOW
        self.frame_count = 0
    
    def process_frame(self, frame):
        """Process a single frame for eye tracking."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detect_faces(frame)
        
        if not self.face_detector.is_face_detected(faces):
            return None
        
        results = {}
        
        for face in faces:
            landmarks = self.face_detector.get_landmarks(gray, face)
            if landmarks is None:
                continue
            
            # Calculate ratios
            l_tb = self.eye_tracker.get_tb_ratio(LEFT_EYE_POINTS, landmarks)
            r_tb = self.eye_tracker.get_tb_ratio(RIGHT_EYE_POINTS, landmarks)
            tb_ratio = (l_tb + r_tb) / 2
            
            l_gaze = self.eye_tracker.get_gaze_ratio(LEFT_EYE_POINTS, landmarks, frame, gray)
            r_gaze = self.eye_tracker.get_gaze_ratio(RIGHT_EYE_POINTS, landmarks, frame, gray)
            side_ratio = (l_gaze + r_gaze) / 2
            
            mouth_ratio = self.eye_tracker.get_mouth_ratio(MOUTH_POINTS, landmarks)
            
            # Apply filtering
            if self.frame_count < MOVING_AVERAGE_WINDOW:
                self.side_buffer[self.frame_count] = side_ratio
                self.tb_buffer[self.frame_count] = tb_ratio
                self.frame_count += 1
            else:
                self.side_buffer = rearrange_circular_buffer(side_ratio, self.side_buffer)
                self.tb_buffer = rearrange_circular_buffer(tb_ratio, self.tb_buffer)
                side_ratio = moving_average(self.side_buffer)
                tb_ratio = moving_average(self.tb_buffer)
            
            # Analyze gaze position
            position_flags = self.gaze_analyzer.analyze_position(side_ratio, tb_ratio)
            mouth_open = self.gaze_analyzer.is_mouth_open(mouth_ratio)
            
            results = {
                'side_ratio': side_ratio,
                'tb_ratio': tb_ratio,
                'mouth_ratio': mouth_ratio,
                'mouth_open': mouth_open,
                'center_flag': position_flags[0],
                'right_flag': position_flags[1],
                'left_flag': position_flags[2],
                'top_flag': position_flags[3],
                'bot_flag': position_flags[4],
                'face_detected': True
            }
            
            break  # Process only the first detected face
        
        return results
    
    def map_gaze_to_buttons(self, results):
        """Map eye tracking results to button controller flags"""
        if not results or not results.get('face_detected', False):
            # No face detected, don't change flags
            return
        
        # Extract flags from eye tracking results
        left_flag = results.get('left_flag', False)
        right_flag = results.get('right_flag', False)
        center_flag = results.get('center_flag', False)
        top_flag = results.get('top_flag', False)
        bot_flag = results.get('bot_flag', False)
        mouth_open = results.get('mouth_open', False)
        
        # Determine which colorFlag should be active based on gaze position
        target_button = None
        
        if left_flag and top_flag:
            target_button = 0  # temp_up
        elif center_flag and top_flag:
            # Do nothing - no button mapping
            pass
        elif right_flag and top_flag:
            target_button = 2  # temp_down
        elif left_flag and bot_flag:
            target_button = 3  # cooling
        elif center_flag and bot_flag:
            target_button = 4  # fan
        elif right_flag and bot_flag:
            target_button = 5  # off
        
        # Update colorFlags in shared memory
        if target_button is not None:
            # Set the target button's colorFlag to True (automatically sets others to False)
            self.memory.update_color_flag(target_button, True)
        else:
            # No valid gaze position, clear all colorFlags
            data = self.memory.read_memory()
            if any(data['color_flags']):
                for i in range(6):
                    if data['color_flags'][i]:
                        self.memory.update_color_flag(i, False)
                        break
        
        # Update secondFlag based on mouth state
        current_data = self.memory.read_memory()
        if mouth_open != current_data['second_flag']:
            self.memory.update_second_flag(mouth_open)
    
    def run(self):
        """Run the main tracking loop."""
        cap = cv2.VideoCapture(0)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                start_time = time.time()
                results = self.process_frame(frame)

                self.map_gaze_to_buttons(results)
                
                if results:
                    # Here you can add your application logic
                    # For example, logging results or controlling external systems
                    print(f"Position flags: {results}")
                
                key = cv2.waitKey(1)
                if key == 27:  # ESC key
                    break
                
        finally:
            cap.release()
            cv2.destroyAllWindows()


def main():
    """Run the eye tracking system."""
    try:
        system = EyeTrackingSystem()
        system.run()
    except FileNotFoundError:
        print("Calibration file not found. Please run calibration first.")
        print("Run: python main_calibration.py")


if __name__ == "__main__":
    main()
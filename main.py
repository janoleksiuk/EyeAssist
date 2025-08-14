"""
Eye Tracker 
by Jan Oleksiuk, 2024

"""

import cv2
import numpy as np
import time
from typing import Tuple
from dataclasses import dataclass

from eye_detection import EyeDetector
from calibration import CalibrationManager
from gui_controller import GUIController
from utils.utils import MovingAverage, FileManager


@dataclass
class AppConfig:
    """Application configuration settings"""
    model_path: str = "model/shape_predictor_68_face_landmarks.dat"
    utils_path: str = "utils"
    calib_file: str = "geo_calib.txt"
    blink_threshold_multiplier: float = 0.875
    filter_size: int = 9
    blink_sleep_duration: float = 0.335


class EyeTrackingApp:
    """Main application class for eye tracking system"""
    
    def __init__(self, config: AppConfig = None):
        self.config = config or AppConfig()
        self.cap = cv2.VideoCapture(0)
        
        # Initialize components
        self.eye_detector = EyeDetector(self.config.model_path)
        self.calib_manager = CalibrationManager(self.config.utils_path)
        self.gui_controller = GUIController(self.config.utils_path)
        self.file_manager = FileManager(self.config.utils_path)
        
        # Initialize filters
        self.side_gaze_filter = MovingAverage(self.config.filter_size)
        self.tb_ratio_filter = MovingAverage(self.config.filter_size)
        
        # Load calibration data
        self.calib_data = self.file_manager.load_calibration_data(self.config.calib_file)
        self.blink_threshold = float(self.calib_data['mouth']) * self.config.blink_threshold_multiplier
        
        # Initialize state
        self.reset_state()
    
    def reset_state(self):
        """Reset application state"""
        self.prev_flags = {'center': 0, 'right': 0, 'left': 0, 'top': 0, 'bot': 0}
        self.blink_flags = {'center': 0, 'right': 0, 'left': 0, 'top': 0, 'bot': 0}
        self.prev_blink_flags = {'center': 0, 'right': 0, 'left': 0, 'top': 0, 'bot': 0}
        self.memory_blink_flags = {'top': 0, 'bot': 0, 'left': 0, 'right': 0, 'center': 0}
        self.memory_color = (115, 115, 115)
        
        self.blink_time = 100
        self.anti_millis_blink = 0
        self.dbl_blink_gui = 0
        self.stop_flag = 1
        self.angle_change_flags = {'dec': 0, 'inc': 0}
        
        # Angle and velocity tracking
        self.current_angle = 1
        self.angle_positions = [0.0, 0.0, 0.0]
        self.angle_velocities = [10, 10, 10]
    
    def process_frame(self, frame: np.ndarray) -> Tuple[bool, dict]:
        """Process a single frame and return face detection status and gaze data"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.eye_detector.detect_faces(gray)
        
        if not faces:
            return False, {}
        
        face = faces[0]  # Use first detected face
        landmarks = self.eye_detector.get_landmarks(gray, face)
        
        # Get eye ratios
        blink_ratio = self.eye_detector.get_blink_ratio(landmarks)
        tb_ratio = self.eye_detector.get_tb_ratio(landmarks)
        side_gaze_ratio = self.eye_detector.get_gaze_ratio(landmarks, frame, gray)
        
        # Apply filtering
        filtered_side_gaze = self.side_gaze_filter.update(side_gaze_ratio)
        filtered_tb_ratio = self.tb_ratio_filter.update(tb_ratio)
        
        return True, {
            'blink_ratio': blink_ratio,
            'tb_ratio': filtered_tb_ratio,
            'side_gaze_ratio': filtered_side_gaze,
            'raw_tb_ratio': tb_ratio,
            'raw_side_gaze': side_gaze_ratio
        }
    
    def determine_gaze_position(self, gaze_data: dict) -> dict:
        """Determine gaze position flags based on ratios and calibration data"""
        flags = {'center': 0, 'right': 0, 'left': 0, 'top': 0, 'bot': 0}
        
        tb_ratio = gaze_data['tb_ratio']
        side_gaze_ratio = gaze_data['side_gaze_ratio']
        
        # Determine vertical position
        if tb_ratio > float(self.calib_data['tb']):
            flags['top'] = 1
            # Determine horizontal position for top
            if side_gaze_ratio < float(self.calib_data['ru']):
                flags['right'] = 1
            elif side_gaze_ratio > float(self.calib_data['lu']):
                flags['left'] = 1
            else:
                flags['center'] = 1
        else:
            flags['bot'] = 1
            # Determine horizontal position for bottom
            if side_gaze_ratio < float(self.calib_data['rd']):
                flags['right'] = 1
            elif side_gaze_ratio > float(self.calib_data['ld']):
                flags['left'] = 1
            else:
                flags['center'] = 1
        
        return flags
    
    def handle_blinking(self, gaze_data: dict, current_flags: dict) -> bool:
        """Handle blink detection and state management"""
        is_blinking = gaze_data['blink_ratio'] > 10000 * self.blink_threshold
        
        if is_blinking:
            self.blink_time = time.time()
            
            # Use previous position flags during blink
            self.blink_flags = self.prev_flags.copy()
            
            # Check for double blink
            if (self.prev_blink_flags == self.blink_flags and 
                self.anti_millis_blink == 0):
                self.dbl_blink_gui = 1
            else:
                self.dbl_blink_gui = 0
            
            self.prev_blink_flags = self.blink_flags.copy()
            self.anti_millis_blink = 1
        else:
            self.anti_millis_blink = 0
            self.prev_flags = current_flags.copy()
        
        return is_blinking
    
    def update_angle_positions(self):
        """Update angle positions based on current state"""
        if self.angle_change_flags['inc']:
            if self.angle_positions[self.current_angle - 1] < 90:
                velocity_factor = self.angle_velocities[self.current_angle - 1] / 300
                self.angle_positions[self.current_angle - 1] += 0.05 + velocity_factor
        
        elif self.angle_change_flags['dec']:
            if self.angle_positions[self.current_angle - 1] > -90:
                velocity_factor = self.angle_velocities[self.current_angle - 1] / 300
                self.angle_positions[self.current_angle - 1] -= 0.05 + velocity_factor
    
    def run(self):
        """Main application loop"""
        print("Starting Eye Tracking System...")
        
        try:
            while True:
                start_time = time.time()
                ret, frame = self.cap.read()
                
                if not ret:
                    print("Failed to capture frame")
                    break
                
                # Process frame
                face_detected, gaze_data = self.process_frame(frame)
                
                if face_detected:
                    # Determine gaze position
                    current_flags = self.determine_gaze_position(gaze_data)
                    
                    # Handle blinking
                    is_blinking = self.handle_blinking(gaze_data, current_flags)
                    
                    # Update GUI with current state
                    self.gui_controller.update_display(
                        current_flags, 
                        self.blink_flags,
                        self.dbl_blink_gui,
                        self.blink_time,
                        self.stop_flag,
                        self.current_angle,
                        self.angle_positions,
                        self.angle_velocities,
                        self.memory_blink_flags,
                        self.memory_color
                    )
                    
                    # Handle GUI interactions
                    action = self.gui_controller.handle_interactions(
                        self.blink_flags,
                        self.dbl_blink_gui,
                        self.current_angle
                    )
                    
                    # Process GUI actions
                    if action:
                        self.process_gui_action(action)
                    
                    # Update angle positions
                    self.update_angle_positions()
                    
                    # Add delay for blink processing
                    if is_blinking:
                        time.sleep(self.config.blink_sleep_duration)
                
                else:
                    # No face detected
                    self.gui_controller.update_display_no_face()
                
                # Display frame
                self.gui_controller.render()
                
                # Performance monitoring
                end_time = time.time()
                fps = 1.0 / (end_time - start_time) if end_time > start_time else 0
                print(f"FPS: {fps:.1f}", end='\r')
                
                # Check for exit
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC key
                    break
        
        except KeyboardInterrupt:
            print("\nShutting down...")
        
        finally:
            self.cleanup()
    
    def process_gui_action(self, action: dict):
        """Process actions from GUI controller"""
        action_type = action.get('type')
        
        if action_type == 'switch_gui':
            self.reset_interaction_state()
        
        elif action_type == 'switch_angle':
            self.current_angle = ((self.current_angle) % 3) + 1
            self.reset_interaction_state()
        
        elif action_type == 'angle_inc':
            self.angle_change_flags['inc'] = 1
            self.angle_change_flags['dec'] = 0
        
        elif action_type == 'angle_dec':
            self.angle_change_flags['inc'] = 0
            self.angle_change_flags['dec'] = 1
        
        elif action_type == 'velocity_inc':
            if self.angle_velocities[self.current_angle - 1] < 100:
                self.angle_velocities[self.current_angle - 1] += 10
            self.reset_interaction_state()
        
        elif action_type == 'velocity_dec':
            if self.angle_velocities[self.current_angle - 1] > 0:
                self.angle_velocities[self.current_angle - 1] -= 10
            self.reset_interaction_state()
        
        elif action_type == 'stop':
            self.stop_flag = 1
            self.angle_change_flags = {'dec': 0, 'inc': 0}
            self.reset_interaction_state()
    
    def reset_interaction_state(self):
        """Reset interaction-related state variables"""
        self.blink_time = 100
        self.prev_blink_flags = {'center': 0, 'right': 0, 'left': 0, 'top': 0, 'bot': 0}
        self.dbl_blink_gui = 0
        self.memory_color = (115, 115, 115)
        self.stop_flag = 0
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Cleanup completed")


def main():
    """Main entry point"""
    config = AppConfig()
    app = EyeTrackingApp(config)
    
    # Run calibration first
    calibration_successful = app.calib_manager.run_calibration()
    
    if calibration_successful:
        # Reload calibration data
        app.calib_data = app.file_manager.load_calibration_data(config.calib_file)
        app.blink_threshold = float(app.calib_data['mouth']) * config.blink_threshold_multiplier
        
        # Run main application
        app.run()
    else:
        print("Calibration failed. Exiting...")


if __name__ == "__main__":
    main()
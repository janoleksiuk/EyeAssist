"""
Calibration Module
Handles the calibration process for eye tracking
"""

import cv2
import numpy as np
import time
import winsound
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from eye_detection import EyeDetector


@dataclass
class CalibrationPoint:
    """Represents a calibration point"""
    name: str
    image_path: str
    pre_image_path: str
    side_values: list
    top_values: list
    
    def __post_init__(self):
        if not self.side_values:
            self.side_values = []
        if not self.top_values:
            self.top_values = []


class CalibrationManager:
    """Manages the calibration process"""
    
    def __init__(self, utils_path: str):
        self.utils_path = Path(utils_path)
        self.eye_detector = EyeDetector("model/shape_predictor_68_face_landmarks.dat")
        self.cap = cv2.VideoCapture(0)
        
        # Calibration state
        self.current_stage = 0
        self.calibration_values = {
            'side': 0.0,
            'top': 0.0,
            'mouth': 0.0
        }
        self.sample_count = 0
        self.timer = 0.0
        
        # Calibration points
        self.calibration_points = {
            'lu': CalibrationPoint('left_up', '1.png', 'pre1.png', [], []),      # stage 2
            'ru': CalibrationPoint('right_up', '2.png', 'pre2.png', [], []),     # stage 4
            'rd': CalibrationPoint('right_down', '3.png', 'pre3.png', [], []),   # stage 6
            'ld': CalibrationPoint('left_down', '4.png', 'pre4.png', [], []),    # stage 8
            'mouth': CalibrationPoint('mouth', '5.png', 'pre5.png', [], [])      # stage 10
        }
        
        # Load calibration images
        self.load_calibration_images()
    
    def load_calibration_images(self):
        """Load all calibration images"""
        self.images = {}
        image_files = {
            'centerline': 'centerline.png',
            'pre_1': 'pre1.png', '1': '1.png',
            'pre_2': 'pre2.png', '2': '2.png',
            'pre_3': 'pre3.png', '3': '3.png',
            'pre_4': 'pre4.png', '4': '4.png',
            'pre_5': 'pre5.png', '5': '5.png'
        }
        
        for key, filename in image_files.items():
            image_path = self.utils_path / filename
            if image_path.exists():
                self.images[key] = cv2.imread(str(image_path), 1)
            else:
                print(f"Warning: Image {filename} not found")
                # Create a placeholder image
                self.images[key] = np.zeros((600, 800, 3), dtype=np.uint8)
                cv2.putText(self.images[key], f"Missing: {filename}", 
                           (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    def display_fullscreen(self, window_name: str, image: np.ndarray):
        """Display image in fullscreen"""
        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow(window_name, image)
    
    def collect_calibration_sample(self, frame: np.ndarray, gray: np.ndarray, point_name: str) -> bool:
        """Collect a calibration sample"""
        faces = self.eye_detector.detect_faces(gray)
        
        if not faces:
            return False
        
        face = faces[0]
        landmarks = self.eye_detector.get_landmarks(gray, face)
        
        # Get measurements
        side_gaze_ratio = self.eye_detector.get_gaze_ratio(landmarks, frame, gray)
        tb_ratio = self.eye_detector.get_tb_ratio(landmarks)
        
        if point_name == 'mouth':
            mouth_ratio = self.eye_detector.get_mouth_ratio(landmarks)
            self.calibration_values['mouth'] += mouth_ratio
        else:
            self.calibration_values['side'] += side_gaze_ratio
            self.calibration_values['top'] += tb_ratio
            
            # Store in calibration point
            if point_name in self.calibration_points:
                self.calibration_points[point_name].side_values.append(side_gaze_ratio)
                self.calibration_points[point_name].top_values.append(tb_ratio)
        
        self.sample_count += 1
        return True
    
    def get_average_values(self, point_name: str) -> Tuple[float, float]:
        """Get average calibration values for a point"""
        if point_name == 'mouth':
            return 0.0, self.calibration_values['mouth'] / self.sample_count
        else:
            side_avg = self.calibration_values['side'] / self.sample_count
            top_avg = self.calibration_values['top'] / self.sample_count
            return side_avg, top_avg
    
    def reset_calibration_values(self):
        """Reset calibration values for next stage"""
        self.calibration_values = {'side': 0.0, 'top': 0.0, 'mouth': 0.0}
        self.sample_count = 0
    
    def get_stage_image(self, stage: int) -> Optional[np.ndarray]:
        """Get the appropriate image for the current stage"""
        stage_images = {
            0: 'centerline',
            1: 'pre_1', 2: '1',
            3: 'pre_2', 4: '2',
            5: 'pre_3', 6: '3',
            7: 'pre_4', 8: '4',
            9: 'pre_5', 10: '5'
        }
        
        image_key = stage_images.get(stage)
        return self.images.get(image_key) if image_key else None
    
    def get_stage_point_name(self, stage: int) -> Optional[str]:
        """Get the calibration point name for the current stage"""
        stage_points = {
            2: 'lu',    # left up
            4: 'ru',    # right up
            6: 'rd',    # right down
            8: 'ld',    # left down
            10: 'mouth' # mouth
        }
        return stage_points.get(stage)
    
    def save_calibration_data(self, results: Dict[str, float]) -> bool:
        """Save calibration data to file"""
        try:
            calib_file = self.utils_path / "geo_calib.txt"
            with open(calib_file, "w") as file:
                # Format: lu_side,ru_side,ld_side,rd_side,tb,mouth
                line = f"{results['lu_side']},{results['ru_side']},{results['ld_side']}," \
                       f"{results['rd_side']},{results['tb']},{results['mouth']}"
                file.write(line)
            return True
        except Exception as e:
            print(f"Error saving calibration data: {e}")
            return False
    
    def run_calibration(self) -> bool:
        """Run the complete calibration process"""
        print("Starting calibration process...")
        
        # Create fullscreen window
        cv2.namedWindow("Calibration", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Calibration", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        calibration_results = {}
        
        try:
            while self.current_stage <= 10:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to capture frame")
                    return False
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Display appropriate image for current stage
                stage_image = self.get_stage_image(self.current_stage)
                if stage_image is not None:
                    cv2.imshow("Calibration", stage_image)
                
                # Handle calibration stages
                if self.current_stage % 2 == 0 and self.current_stage != 0:
                    # Data collection stages (2, 4, 6, 8, 10)
                    point_name = self.get_stage_point_name(self.current_stage)
                    
                    if point_name:
                        success = self.collect_calibration_sample(frame, gray, point_name)
                        if success:
                            # Show progress
                            print(f"Collecting {point_name} data... Samples: {self.sample_count}")
                    
                    # Auto-advance after 3 seconds
                    if time.time() - self.timer > 2.9:
                        if point_name:
                            side_avg, top_avg = self.get_average_values(point_name)
                            
                            if point_name == 'mouth':
                                calibration_results['mouth'] = top_avg
                            else:
                                calibration_results[f'{point_name}_side'] = side_avg
                                calibration_results[f'{point_name}_top'] = top_avg
                        
                        # Play sound for completion
                        if self.current_stage == 10:
                            try:
                                winsound.Beep(500, 700)
                            except:
                                print("Calibration complete!")
                        
                        self.advance_stage()
                
                else:
                    # Instruction/preparation stages
                    key = cv2.waitKey(1) & 0xFF
                    if key == 27:  # ESC key
                        self.advance_stage()
                
                # Check for manual exit
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Calibration cancelled by user")
                    return False
            
            # Calculate final calibration values
            tb_average = (calibration_results.get('lu_top', 0) + 
                         calibration_results.get('ru_top', 0) + 
                         calibration_results.get('rd_top', 0) + 
                         calibration_results.get('ld_top', 0)) / 4
            
            final_results = {
                'lu_side': calibration_results.get('lu_side', 0),
                'ru_side': calibration_results.get('ru_side', 0),
                'ld_side': calibration_results.get('ld_side', 0),
                'rd_side': calibration_results.get('rd_side', 0),
                'tb': tb_average,
                'mouth': calibration_results.get('mouth', 0)
            }
            
            # Save calibration data
            success = self.save_calibration_data(final_results)
            if success:
                print("Calibration completed successfully!")
                print(f"Results: {final_results}")
            else:
                print("Failed to save calibration data")
                return False
            
            return True
        
        except Exception as e:
            print(f"Calibration error: {e}")
            return False
        
        finally:
            #cv2.destroyWindow("Calibration")
            if self.cap:
                self.cap.release()
    
    def advance_stage(self):
        """Advance to the next calibration stage"""
        self.current_stage += 1
        self.reset_calibration_values()
        cv2.destroyWindow("Calibration")
        self.timer = time.time()
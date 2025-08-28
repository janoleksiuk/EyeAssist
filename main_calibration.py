"""Main calibration application."""

import cv2
from face_tracker.face_detector import FaceDetector
from face_tracker.eye_tracker import EyeTracker
from face_tracker.calibration import CalibrationSystem


def main():
    """Run the calibration process."""
    cap = cv2.VideoCapture(0)
    
    face_detector = FaceDetector()
    eye_tracker = EyeTracker()
    calibration = CalibrationSystem(eye_tracker, face_detector)
    
    try:
        while not calibration.is_complete():
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            calibration.process_frame(frame, gray)
            calibration.update_display()
            calibration.handle_timing()
            
            key = cv2.waitKey(1)
            calibration.handle_keypress(key)
        
        calibration.finalize_calibration()
        print("Calibration completed successfully!")
        
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

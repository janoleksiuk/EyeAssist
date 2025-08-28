"""Configuration constants for the eye tracking system."""

# Face landmark indices
LEFT_EYE_POINTS = [36, 37, 38, 39, 40, 41]
RIGHT_EYE_POINTS = [42, 43, 44, 45, 46, 47]
MOUTH_POINTS = [62, 66, 60, 64]

# Calibration settings
CALIBRATION_DURATION = 2.9  # seconds
MOVING_AVERAGE_WINDOW = 9
MOUTH_THRESHOLD_MULTIPLIER = 0.8

# File paths
SHAPE_PREDICTOR_PATH = "model/shape_predictor_68_face_landmarks.dat"
CALIBRATION_FILE = "utils/geo_calib.txt"

# Image paths
CALIBRATION_IMAGES = {
    'centerline': 'utils/centerline.png',
    'pre_1': 'utils/pre1.png',
    'stage_1': 'utils/1.png',
    'pre_2': 'utils/pre2.png',
    'stage_2': 'utils/2.png',
    'pre_3': 'utils/pre3.png',
    'stage_3': 'utils/3.png',
    'pre_4': 'utils/pre4.png',
    'stage_4': 'utils/4.png',
    'pre_5': 'utils/pre5.png',
    'stage_5': 'utils/5.png'
}

# Sound settings
CALIBRATION_COMPLETE_FREQUENCY = 500
CALIBRATION_COMPLETE_DURATION = 700
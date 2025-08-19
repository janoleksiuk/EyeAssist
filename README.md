# Eye-Gaze-Based Human-Machine Interface Framework

A low-cost eye-tracking solution for controlling assistive devices to improve quality of life and independence of individuals with impaired mobility. This HMI framework can be easily adopted to a wide variety of assistive devices - examples of use cases presented below (assistive, powered wheelchair, smart-home).

## Overview

This system provides an accessible alternative to expensive eye-tracking devices by using a standard video camera for gaze detection and blink recognition. It enables direct control of a 5-DOF upper extremity powered rehabilitation exoskeleton through eye movements and blinking patterns. Can be adopted to be used without IR cameras usually used in eye-tracking systems. Example usecases presented below:


<img width="969" height="627" alt="usecase2" src="https://github.com/user-attachments/assets/ecf2a8b8-7383-4fa6-a1cb-6cc739d0c412" />
<img width="969" height="627" alt="usecase4" src="https://github.com/user-attachments/assets/bc0b751d-4715-446b-9729-a6d17ce451fa" />

Read more about the system [here](https://doi.org/10.21203/rs.3.rs-6006333/v1)

**Key Features:**
- Low-cost video camera-based eye tracking
- Real-time gaze detection and blink recognition
- Intuitive GUI for rehabilitation robot control
- Calibration system for individual user adaptation

## System Requirements

### Hardware
- Standard USB camera (webcam)
- Computer with sufficient processing power for real-time video processing

### Software
- Python 3.7+
- OpenCV 
- NumPy
- dlib
- Windows OS (for `winsound` module)
(see requirements.txt)

### Models
- dlib's 68-point facial landmark predictor model (`shape_predictor_68_face_landmarks.dat`)

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-repo/eye-gaze-exoskeleton
cd eye-assist
```

2. **Install required packages:**
```bash
pip install opencv-python numpy dlib
```

3. **Download the dlib model:**
   - Download `shape_predictor_68_face_landmarks.dat` from dlib's official repository
   - Place it in the `model/` directory

4. **Create necessary directories:**
```bash
mkdir -p utils model logs config
```

5. **Add calibration images:**
   - Place GUI images (`gui1.png`, `gui2.png`, `gui3.png`) in `utils/`
   - Place calibration images (`centerline.png`, `pre1.png`, `1.png`, etc.) in `utils/`

## Usage

### 1. Run the Complete System
```bash
python main.py
```
This will first run the calibration process, then start the main eye-tracking application.

### 2. Calibration Process
The system guides users through a 5-point calibration:
- **Centerline alignment**
- **Left-up gaze point**
- **Right-up gaze point** 
- **Right-down gaze point**
- **Left-down gaze point**
- **Blink calibration** (for blink threshold)

Press `ESC` to advance through calibration stages.

### 3. Control Interface
The system provides three GUI modes:

#### GUI 1 - Angle Control
- **Top-Center**: Neutral zone 
- **Top-Left**: Increase current angle position
- **Top-Right**: Decrease current angle position
- **Bottom-Center**: Switch between angles (1, 2, 3)
- **Bottom-Left**: Switch to GUI 2
- **Bottom-Right**: Stop movement

#### GUI 2 - Velocity Control
- **Top-Center**: Neutral zone 
- **Top-Left**: Increase velocity (10% increments)
- **Top-Right**: Decrease velocity (10% decrements)
- **Bottom-Left**: Switch to GUI 1
- **Bottom-Center**: Switch to GUI 3
- **Bottom-Right**: Stop movement

#### GUI 3 - Additional Functions
- **Top-Center**: Neutral zone 
- **Bottom-Left**: Return to GUI 1
- **Bottom-Right**: Stop movement

### 4. Interaction Method
- **Single Blink**: Highlight button (red border)
- **Double Blink**: Execute action (green border)
- **Gaze Direction**: Navigate between buttons

GUI usage example photo:

<img width="475" height="328" alt="Zrzut ekranu 2025-08-16 214724" src="https://github.com/user-attachments/assets/fefef06a-e676-4cfb-bba6-c977a255e73b" />

## Project Structure

```
eye-gaze-exoskeleton/
├── main.py      # Main application entry point
├── eye_detection.py         # Eye detection and gaze tracking
├── calibration.py          # Calibration system
├── gui_controller.py       # GUI management and interactions
├── model/
│   └── shape_predictor_68_face_landmarks.dat
├── utils/
│   ├── gui1.png           # GUI interface images
│   ├── gui2.png
│   ├── gui3.png
|   ├── utils.py               # Utility classes and functions
│   ├── centerline.png     # Calibration images
│   ├── pre1.png - pre5.png
│   ├── 1.png - 5.png
│   └── geo_calib.txt      # Calibration data (generated)
```

**Note**: This system is intended for research and rehabilitation purposes. Always ensure proper supervision and safety protocols when used with actual exoskeleton hardware.

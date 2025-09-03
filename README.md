# EyeAssist 

**Human-Machine Interface based on eye gaze and mouth motion tracking.**

## Overview

A low-cost face-tracking solution for controlling assistive devices to **improve quality of life and independence of individuals with impaired mobility** who are not able to operate with typical control interfaces based on buttons and joysticks. This system provides an accessible alternative to expensive eye-tracking devices by using a standard video camera for gaze detection and mouth motion recognition. It enables direct control of any adopted GUI that consist of 6 buttons per panel. Does not require IR cameras usually used in eye-tracking systems. This HMI framework can be easily adopted to a wide variety of assistive devices - examples of use cases presented below (assistive systems, smart-home, robots etc.). Read more about the system utilisation to control rehabilitation robot [here](https://doi.org/10.21203/rs.3.rs-6006333/v1).

**Key Features:**
- Real-time eye-tracking and mouth motion recognition based on dlib `shape_predictor_68_face_landmarks` [model](https://github.com/davisking/dlib).
- Intuitive GUI (included example interactive AC GUI panel)
- Calibration system for individual user adaptation


## Use case

User is located in front of the screen which is displaying the GUI of a given system. The system allows them to select the appropriate virtual button using their gaze, while its activation is triggered by opening the mouth. The example usecases are presented below:

<p align="center">
  <img src="https://github.com/user-attachments/assets/bc0b751d-4715-446b-9729-a6d17ce451fa" width="50%" />
  <img src="https://github.com/user-attachments/assets/fefef06a-e676-4cfb-bba6-c977a255e73b" width="44.3%" />
</p>

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/janoleskiuk/EyeAssist.git
cd EyeAssist
```

2. **Install required packages:**
```bash
python -m pip install -r requirements.txt
```

3. **Install `dlib` package:**
```bash
cd dlib
python -m pip install dlib-19.24.99-cp312-cp312-win_amd64.whl
```
**Note**: This .whl file is compatibile with python version 3.12. If you are using other python version download suitable .whl file from this [repository](https://github.com/z-mahmud22/Dlib_Windows_Python3.x).

## Usage

1. **Launch calibration**
```bash
python main_calibration.py
```

2. **Launch face tracker**

After succesful calibration run:
```bash
python main_tracker.py
```

3. **Launch GUI**

Open another terminal and run:
```bash
python main_GUI.py
```

## Project Structure
```
src/
├── config/                 # Configuration files of the system
├── data/                   # Data exchanged by system modules
├── dlib/                   # dlib .whl file
├── face_tracker/           # Modules responsible for face tracking
├── gui/                    # GUI modules
├── models/                 # dlib 68-point facial recognition model
├── utils/                  # Utilities
├── main_calibration.py     # Calibration program
├── main_GUI.py             # GUI program
├── main_tracker.py         # Face tracker program
```

---


**Note**: This system is intended for research and education purposes. Always ensure proper supervision and safety protocols when used with actual hardware.

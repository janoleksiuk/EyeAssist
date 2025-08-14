"""
Utilities Module
Contains utility classes and functions for the eye tracking system
"""

import numpy as np
from pathlib import Path
from typing import List, Dict, Optional


class MovingAverage:
    """Moving average filter for smoothing sensor data"""
    
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.values = [0.0] * window_size
        self.index = 0
        self.count = 0
    
    def update(self, new_value: float) -> float:
        """Update the filter with a new value and return the filtered result"""
        if self.count < self.window_size:
            # Still filling up the initial buffer
            self.values[self.count] = new_value
            self.count += 1
            return sum(self.values[:self.count]) / self.count
        else:
            # Circular buffer is full, start overwriting
            self.values[self.index] = new_value
            self.index = (self.index + 1) % self.window_size
            return sum(self.values) / self.window_size
    
    def reset(self):
        """Reset the filter"""
        self.values = [0.0] * self.window_size
        self.index = 0
        self.count = 0
    
    def is_initialized(self) -> bool:
        """Check if the filter has enough samples"""
        return self.count >= self.window_size


class RingBuffer:
    """Ring buffer implementation for efficient data storage"""
    
    def __init__(self, size: int):
        self.size = size
        self.buffer = [0.0] * size
        self.index = 0
        self.full = False
    
    def append(self, value: float):
        """Add a value to the buffer"""
        self.buffer[self.index] = value
        self.index = (self.index + 1) % self.size
        if self.index == 0:
            self.full = True
    
    def get_all(self) -> List[float]:
        """Get all values in chronological order"""
        if not self.full:
            return self.buffer[:self.index]
        return self.buffer[self.index:] + self.buffer[:self.index]
    
    def get_last_n(self, n: int) -> List[float]:
        """Get the last n values"""
        all_values = self.get_all()
        return all_values[-n:] if len(all_values) >= n else all_values
    
    def mean(self) -> float:
        """Calculate mean of all stored values"""
        values = self.get_all()
        return sum(values) / len(values) if values else 0.0
    
    def is_full(self) -> bool:
        """Check if buffer is full"""
        return self.full


class FileManager:
    """Handles file operations for the eye tracking system"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def load_calibration_data(self, filename: str) -> Dict[str, str]:
        """Load calibration data from file"""
        calib_file = self.base_path / filename
        
        if not calib_file.exists():
            print(f"Calibration file {calib_file} not found")
            return self.get_default_calibration()
        
        try:
            with open(calib_file, 'r') as file:
                line = file.readline().strip()
                values = line.split(',')
                
                if len(values) >= 6:
                    return {
                        'lu': values[0],  # left up side
                        'ru': values[1],  # right up side
                        'ld': values[2],  # left down side
                        'rd': values[3],  # right down side
                        'tb': values[4],  # top bottom ratio
                        'mouth': values[5]  # mouth ratio
                    }
                else:
                    print(f"Invalid calibration file format")
                    return self.get_default_calibration()
        
        except Exception as e:
            print(f"Error loading calibration data: {e}")
            return self.get_default_calibration()
    
    def get_default_calibration(self) -> Dict[str, str]:
        """Get default calibration values"""
        return {
            'lu': '0.8',    # left up
            'ru': '1.2',    # right up  
            'ld': '0.8',    # left down
            'rd': '1.2',    # right down
            'tb': '1.0',    # top bottom threshold
            'mouth': '0.5'  # mouth threshold
        }
    
    def save_calibration_data(self, data: Dict[str, float], filename: str) -> bool:
        """Save calibration data to file"""
        calib_file = self.base_path / filename
        
        try:
            with open(calib_file, 'w') as file:
                line = f"{data['lu']},{data['ru']},{data['ld']},{data['rd']},{data['tb']},{data['mouth']}"
                file.write(line)
            return True
        except Exception as e:
            print(f"Error saving calibration data: {e}")
            return False
    
    def log_session_data(self, data: Dict, filename: str = None):
        """Log session data for analysis"""
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}.log"
        
        log_file = self.base_path / filename
        
        try:
            with open(log_file, 'a') as file:
                import json
                file.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"Error logging session data: {e}")

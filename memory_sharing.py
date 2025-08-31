#!/usr/bin/env python3
"""
Memory Sharing Library - Simple shared memory implementation using file-based storage
"""

import json
import os
import time
from threading import Lock

class MemoryShare:
    def __init__(self, memory_file="shared_memory.json"):
        self.memory_file = memory_file
        self.lock = Lock()
        
        # Initialize memory file if it doesn't exist
        if not os.path.exists(self.memory_file):
            self.write_memory({
                'color_flags': [False] * 6,
                'second_flag': False
            })
    
    def read_memory(self):
        """Read shared memory data"""
        try:
            with self.lock:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default values if file doesn't exist or is corrupted
            default_data = {
                'color_flags': [False] * 6,
                'second_flag': False
            }
            self.write_memory(default_data)
            return default_data
    
    def write_memory(self, data):
        """Write data to shared memory"""
        with self.lock:
            with open(self.memory_file, 'w') as f:
                json.dump(data, f)
    
    def update_color_flag(self, button_index, value):
        """Update specific colorFlag with mutex protection"""
        if 0 <= button_index < 6:
            data = self.read_memory()
            if bool(value):
                # If setting to True, set all others to False
                data['color_flags'] = [False] * 6
                data['color_flags'][button_index] = True
            else:
                # If setting to False, just set this one to False
                data['color_flags'][button_index] = False
            self.write_memory(data)
    
    def update_second_flag(self, value):
        """Update secondFlag with mutex protection"""
        data = self.read_memory()
        data['second_flag'] = bool(value)
        self.write_memory(data)
    
    def toggle_color_flag(self, button_index):
        """Toggle colorFlag for specified button"""
        if 0 <= button_index < 6:
            data = self.read_memory()
            if data['color_flags'][button_index]:
                # Currently True, set to False
                data['color_flags'][button_index] = False
            else:
                # Currently False, set to True and set all others to False
                data['color_flags'] = [False] * 6
                data['color_flags'][button_index] = True
            self.write_memory(data)
    
    def toggle_second_flag(self):
        """Toggle secondFlag"""
        data = self.read_memory()
        data['second_flag'] = not data['second_flag']
        self.write_memory(data)
    
    def get_buttons_to_click(self):
        """Return list of button indices that should be clicked"""
        data = self.read_memory()
        if data['second_flag']:
            return [i for i in range(6) if data['color_flags'][i]]
        return []
    
    def cleanup(self):
        """Clean up shared memory file"""
        try:
            if os.path.exists(self.memory_file):
                os.remove(self.memory_file)
        except:
            pass
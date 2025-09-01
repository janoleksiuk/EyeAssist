#!/usr/bin/env python3
"""
Button Controller - Uses shared memory for flag management
"""

import time
from utils.data_sharing import DataShare

class ButtonController:
    def __init__(self):
        """Initialize with shared memory"""
        self.data = DataShare()
        print("ButtonController initialized with shared memory")
        print("- 6 colorFlag variables (brightness control)")
        print("- 1 secondFlag variable (clicks buttons where colorFlag is True)")
    
    # ColorFlag methods - control brightness
    def get_color_flag(self, button_index):
        """Get colorFlag for specified button (0-5)"""
        if 0 <= button_index < 6:
            data = self.data.read_memory()
            return data['color_flags'][button_index]
        return False
    
    def set_color_flag(self, button_index, value):
        """Set colorFlag for specified button (0-5)"""
        if 0 <= button_index < 6:
            self.data.update_color_flag(button_index, value)
            data = self.data.read_memory()
            print(f"Button {button_index} colorFlag set to {data['color_flags'][button_index]}")
    
    def toggle_color_flag(self, button_index):
        """Toggle colorFlag for specified button (0-5)"""
        if 0 <= button_index < 6:
            self.data.toggle_color_flag(button_index)
            data = self.data.read_memory()
            print(f"Button {button_index} colorFlag toggled to {data['color_flags'][button_index]}")
    
    # SecondFlag methods - control "clicking"
    def get_second_flag(self):
        """Get the single secondFlag"""
        data = self.data.read_memory()
        return data['second_flag']
    
    def set_second_flag(self, value):
        """Set the single secondFlag"""
        self.data.update_second_flag(value)
        data = self.data.read_memory()
        print(f"secondFlag set to {data['second_flag']}")
    
    def toggle_second_flag(self):
        """Toggle the single secondFlag"""
        self.data.toggle_second_flag()
        data = self.data.read_memory()
        print(f"secondFlag toggled to {data['second_flag']}")
    
    def get_buttons_to_click(self):
        """Return list of button indices that should be clicked"""
        return self.data.get_buttons_to_click()
    
    # Utility methods
    def reset_all_flags(self):
        """Reset all boolean variables to False"""
        self.data.write_memory({
            'color_flags': [False] * 6,
            'second_flag': False
        })
        print("All flags reset to False")
    
    def get_all_flags(self):
        """Return all flag states as a dictionary"""
        return self.data.read_memory()
    
    def print_status(self):
        """Print current status of all flags"""
        data = self.data.read_memory()
        print("\n=== Button Controller Status ===")
        for i in range(6):
            print(f"Button {i}: colorFlag={data['color_flags'][i]}")
        print(f"secondFlag={data['second_flag']}")
        print("===============================\n")

def main():
    """Run button controller as standalone program"""
    controller = ButtonController()
    
    print("Button Controller running...")
    print("This program manages shared memory for button flags")
    
    try:
        while True:
            controller.print_status()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nButton Controller stopped")
        controller.memory.cleanup()

if __name__ == "__main__":
    main()
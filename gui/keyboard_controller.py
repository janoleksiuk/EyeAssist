#!/usr/bin/env python3
"""
Keyboard Controller - Handles keyboard input and updates shared memory
"""

import tkinter as tk
import time
from utils.data_sharing import DataShare

class KeyboardController:
    def __init__(self):
        """Initialize keyboard controller with shared memory"""
        self.memory = DataShare()
        
        # Create invisible window for keyboard capture
        self.root = tk.Tk()
        self.root.title("Keyboard Controller")
        self.root.geometry("400x300")
        self.root.configure(bg='#1a1a1a')
        
        # Create simple display
        self.create_display()
        
        # Bind keyboard events
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.focus_set()
        
        # Start continuous display update
        self.update_display()
        
        print("Keyboard Controller started")
        print("Keys 1-6: Toggle colorFlag for buttons 0-5")
        print("Key 7: Toggle secondFlag")
    
    def create_display(self):
        """Create simple display for keyboard controller"""
        title = tk.Label(
            self.root,
            text="Keyboard Controller",
            font=('Arial', 16, 'bold'),
            bg='#1a1a1a',
            fg='white'
        )
        title.pack(pady=10)
        
        instructions = tk.Label(
            self.root,
            text="Keys 1-6: Toggle colorFlag\nKey 7: Toggle secondFlag",
            font=('Arial', 12),
            bg='#1a1a1a',
            fg='yellow'
        )
        instructions.pack(pady=10)
        
        self.status_label = tk.Label(
            self.root,
            text="",
            font=('Courier', 10),
            bg='#1a1a1a',
            fg='green',
            justify='left'
        )
        self.status_label.pack(pady=10, expand=True)
    
    def on_key_press(self, event):
        """Handle keyboard input"""
        key = event.char
        
        # Keys 1-6 toggle colorFlag for buttons 0-5
        if key in '123456':
            button_index = int(key) - 1
            self.memory.toggle_color_flag(button_index)
            print(f"Key '{key}' pressed - Toggled colorFlag for button {button_index}")
        
        # Key 7 toggles secondFlag
        elif key == '7':
            self.memory.toggle_second_flag()
            print(f"Key '7' pressed - Toggled secondFlag")
    
    def update_display(self):
        """Continuously update the display"""
        data = self.memory.read_memory()
        
        status_text = "Shared Memory Status:\n\n"
        
        # Show which colorFlag is active
        active_button = None
        for i in range(6):
            if data['color_flags'][i]:
                active_button = i
                break
        
        if active_button is not None:
            status_text += f"Active colorFlag: Button {active_button}\n"
        else:
            status_text += "No colorFlag active\n"
        
        status_text += f"secondFlag: {'ON' if data['second_flag'] else 'OFF'}\n\n"
        
        # Show which buttons would be clicked
        buttons_to_click = self.memory.get_buttons_to_click()
        if buttons_to_click:
            status_text += f"Will click buttons: {buttons_to_click}"
        else:
            status_text += "No buttons will be clicked"
        
        self.status_label.config(text=status_text)
        
        # Schedule next update
        self.root.after(100, self.update_display)
    
    def run(self):
        """Start the keyboard controller"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nKeyboard Controller stopped")
        finally:
            self.memory.cleanup()

def main():
    controller = KeyboardController()
    controller.run()

if __name__ == "__main__":
    main()

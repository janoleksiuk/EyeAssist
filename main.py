#!/usr/bin/env python3
"""
Main Program - Launches GUI with shared memory integration
"""

import tkinter as tk
from GUI_shared import GUI
import subprocess
import sys
import os

def main():
    """Main function that launches the GUI"""
    
    print("=== HMI System Starting ===")
    print("Components:")
    print("1. GUI (main interface)")
    print("2. Shared memory system")
    print("3. To control via keyboard, run: python keyboard_controller.py")
    print("4. To monitor flags, run: python button_controller_shared.py")
    print("=============================\n")
    
    # Create and run GUI
    root = tk.Tk()
    app = GUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    finally:
        # Cleanup shared memory
        if hasattr(app, 'memory'):
            app.memory.cleanup()
        print("Program terminated")

if __name__ == "__main__":
    main()

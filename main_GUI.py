#!/usr/bin/env python3
"""
Main Program - Launches GUI with shared memory integration
"""

import tkinter as tk
from gui.GUI import GUI

def main():
    """Main function that launches the GUI"""
    
    print("=== HMI System Starting ===")

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

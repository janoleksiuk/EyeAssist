import tkinter as tk
from utils.data_sharing import DataShare

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HMI")
        self.root.geometry("1600x1200")
        self.root.configure(bg='#2c2c2c')
        
        # Make fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.state('zoomed')  # For Windows
        self.root.bind('<Escape>', self.toggle_fullscreen)
        
        # Initialize shared data
        self.data = DataShare()
        
        # Adjustable variables (initialize before creating buttons)
        self.current_temp = 27
        self.current_mode = "COOLING"
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg='#2c2c2c')
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create buttons dictionary
        self.buttons = {}
        
        # Create the GUI layout
        self.create_buttons()
        
        # Start the update loop
        self.update_buttons()
    
    def create_buttons(self):
        """Create all 6 buttons with wide spacing across fullscreen"""

        # Configure main frame grid to use full screen space
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=2) 
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)

        # Top row buttons with wide spacing
        self.buttons['temp_up'] = self.create_button(
            self.main_frame, "TEMPERATURE UP", "▲", 0, 0
        )

        self.buttons['neutral'] = self.create_display_button(
            self.main_frame, "NEUTRAL ZONE", f"CURRENT TEMP: {self.current_temp}°C\nMODE: {self.current_mode}", 0, 1
        )

        self.buttons['temp_down'] = self.create_button(
            self.main_frame, "TEMPERATURE DOWN", "▼", 0, 2
        )

        # Bottom row buttons with wide spacing
        self.buttons['cooling'] = self.create_button(
            self.main_frame, "COOLING", "", 2, 0
        )

        self.buttons['fan'] = self.create_button(
            self.main_frame, "FAN", "", 2, 1
        )

        self.buttons['off'] = self.create_button(
            self.main_frame, "OFF", "", 2, 2, bg_color='#cc3333'
        )
    
    def create_button(self, parent, text, symbol, row, col, bg_color='#ffaa33'):
        """Create a standard button"""
        btn = tk.Button(
            parent,
            text=f"{symbol}\n{text}" if symbol else text,
            font=('Arial', 24, 'bold'),
            bg=bg_color,
            fg='black',
            width=30,
            height=15,
            relief='raised',
            bd=3
        )
        btn.grid(row=row, column=col, padx=50, pady=50, sticky='nsew', ipadx=20, ipady=20)
        
        # Configure grid weights
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        return btn
    
    def create_display_button(self, parent, title, info, row, col):
        """Create the neutral zone display button"""
        btn = tk.Button(
            parent,
            text=f"{title}\n\n\n\n{info}",
            font=('Arial', 24, 'bold'),
            bg='#4da6ff',
            fg='black',
            width=15,
            height=6,
            relief='raised',
            bd=3
        )
        btn.grid(row=row, column=col, padx=50, pady=50, sticky='nsew', ipadx=20, ipady=20)
        
        # Configure grid weights
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        return btn
    
    def update_buttons(self):
        """Update button appearances based on shared memory flags"""
        button_names = ['temp_up', 'neutral', 'temp_down', 'cooling', 'fan', 'off']
        data = self.data.read_memory()
        
        for i, btn_name in enumerate(button_names):
            if btn_name in self.buttons:
                btn = self.buttons[btn_name]
                
                # Get the default colors
                if btn_name == 'neutral':
                    default_bg = '#4da6ff'
                elif btn_name == 'off':
                    default_bg = '#cc3333'
                else:
                    default_bg = '#ffaa33'
                
                # Apply color changes based on flags
                current_bg = default_bg
                
                # Check colorFlag - decrease brightness
                if data['color_flags'][i]:
                    current_bg = self.darken_color(default_bg)
                
                # Update button color
                btn.configure(bg=current_bg)
                
                # Check if this button should be clicked
                buttons_to_click = self.data.get_buttons_to_click()
                if i in buttons_to_click:
                    btn.configure(relief='sunken')
                    # Simulate click action
                    self.handle_button_click(btn_name)
                else:
                    btn.configure(relief='raised')
        
        # Schedule next update
        self.root.after(100, self.update_buttons)
    
    def darken_color(self, color):
        """Darken a hex color by reducing brightness"""
        if color.startswith('#'):
            color = color[1:]
        
        # Convert hex to RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16) 
        b = int(color[4:6], 16)
        
        # Reduce brightness by 30%
        r = int(r * 0.7)
        g = int(g * 0.7)
        b = int(b * 0.7)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def handle_button_click(self, button_name):
        """Handle button click actions"""
        print(f"Button {button_name} was 'clicked' via secondFlag")
        
        if button_name == 'off':
            print("OFF button clicked - Terminating program")
            self.data.cleanup()
            self.root.quit()
            self.root.destroy()
        elif button_name == 'temp_up':
            self.current_temp += 1
            self.update_temperature_display()
            print(f"Temperature increased to {self.current_temp}°C")
        elif button_name == 'temp_down':
            self.current_temp -= 1
            self.update_temperature_display()
            print(f"Temperature decreased to {self.current_temp}°C")
        elif button_name == 'fan':
            self.current_mode = "FAN"
            self.update_temperature_display()
            print(f"Mode changed to {self.current_mode}")
        elif button_name == 'cooling':
            self.current_mode = "COOLING"
            self.update_temperature_display()
            print(f"Mode changed to {self.current_mode}")
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode with Escape key"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)

    def update_temperature_display(self):
        """Update the temperature display on the neutral zone button"""
        if 'neutral' in self.buttons:
            self.buttons['neutral'].configure(
                text=f"Neutral Zone\n\nCURRENT TEMP: {self.current_temp}°C\nMODE: {self.current_mode}"
            )
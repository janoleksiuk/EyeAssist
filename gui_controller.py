"""
GUI Controller Module
Handles the graphical user interface and user interactions
"""

import cv2
import numpy as np
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class GUIState:
    """Represents the current GUI state"""
    current_gui: int = 1
    button_height: int = 308
    button_width: int = 334
    border_thickness: int = 20
    border_offset: int = 20


class GUIController:
    """Manages GUI display and interactions"""
    
    def __init__(self, utils_path: str):
        self.utils_path = Path(utils_path)
        self.state = GUIState()
        
        # Load GUI images
        self.load_gui_images()
        
        # Current display image
        self.current_image = self.gui_images[1].copy()
        
        # Create fullscreen window
        cv2.namedWindow("EyeTracker", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("EyeTracker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Colors
        self.colors = {
            'inactive': (115, 115, 115),
            'active': (255, 145, 0),
            'blink_first': (0, 0, 255),
            'blink_second': (0, 255, 0),
            'angle_display': (178, 151, 0),
            'text_bg': (166, 166, 166),
            'text_color': (30, 30, 30),
            'value_text': (38, 38, 38)
        }
    
    def load_gui_images(self):
        """Load all GUI images"""
        self.gui_images = {}
        
        for i in range(1, 4):
            image_path = self.utils_path / f"gui{i}.png"
            if image_path.exists():
                self.gui_images[i] = cv2.imread(str(image_path), 1)
            else:
                print(f"Warning: GUI image {image_path} not found")
                # Create placeholder
                self.gui_images[i] = np.zeros((1080, 1920, 3), dtype=np.uint8)
                cv2.putText(self.gui_images[i], f"GUI {i} Missing", 
                           (800, 500), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    def draw_button_border(self, image: np.ndarray, x0: int, x1: int, y0: int, y1: int, 
                          thickness: int, color: Tuple[int, int, int]):
        """Draw button border"""
        # Top and bottom borders
        image[y0:y0+thickness, x0:x1] = color
        image[y1-thickness:y1, x0:x1] = color
        
        # Left and right borders
        image[y0+thickness:y1-thickness, x0:x0+thickness] = color
        image[y0+thickness:y1-thickness, x1-thickness:x1] = color
    
    def update_button_display(self, image: np.ndarray, flags: Dict[str, int], 
                             color: Tuple[int, int, int]):
        """Update button display based on gaze flags"""
        h, w = image.shape[:2]
        bw, bh = self.state.button_width, self.state.button_height
        d, offset = self.state.border_thickness, self.state.border_offset
        
        # Button positions
        positions = {
            'left_top': (0+offset, bw, 0+offset, bh),
            'left_bottom': (0+offset, bw, h-bh, h-offset),
            'center_top': (int(w/2)-int(bw/2), int(w/2)+int(bw/2), 0+offset, bh),
            'center_bottom': (int(w/2)-int(bw/2), int(w/2)+int(bw/2), h-bh, h-offset),
            'right_top': (w-bw, w-offset, 0+offset, bh),
            'right_bottom': (w-bw, w-offset, h-bh, h-offset)
        }
        
        # Determine active button
        active_button = None
        if flags['right'] and flags['top']:
            active_button = 'right_top'
        elif flags['right'] and flags['bot']:
            active_button = 'right_bottom'
        elif flags['center'] and flags['top']:
            active_button = 'center_top'
        elif flags['center'] and flags['bot']:
            active_button = 'center_bottom'
        elif flags['left'] and flags['top']:
            active_button = 'left_top'
        elif flags['left'] and flags['bot']:
            active_button = 'left_bottom'
        
        # Draw all buttons
        for button_name, (x0, x1, y0, y1) in positions.items():
            button_color = color if button_name == active_button else self.colors['inactive']
            self.draw_button_border(image, x0, x1, y0, y1, d, button_color)
    
    def update_gui1_display(self, image: np.ndarray, angle: int, angle_positions: list):
        """Update GUI 1 specific display elements"""
        # Clear angle display area
        image[875:1025, 960:1100] = self.colors['angle_display']
        image[157:187, 970:1072] = self.colors['text_bg']
        
        # Display current angle
        cv2.putText(image, str(angle), (965, 1013), 
                   cv2.FONT_HERSHEY_PLAIN, 11, self.colors['text_color'], 15)
        
        # Display angle position
        position_text = f'{angle_positions[angle-1]:.1f}'
        cv2.putText(image, position_text, (979, 185), 
                   cv2.FONT_HERSHEY_PLAIN, 2, self.colors['value_text'], 2)
    
    def update_gui2_display(self, image: np.ndarray, angle: int, angle_velocities: list):
        """Update GUI 2 specific display elements"""
        # Clear velocity display area
        image[157:187, 970:1070] = self.colors['text_bg']
        
        # Display angular velocity
        velocity_text = f"{angle_velocities[angle-1]}%"
        cv2.putText(image, velocity_text, (990, 185), 
                   cv2.FONT_HERSHEY_PLAIN, 2, self.colors['value_text'], 2)
    
    def update_display(self, current_flags: Dict[str, int], blink_flags: Dict[str, int],
                      dbl_blink_gui: int, blink_time: float, stop_flag: int,
                      current_angle: int, angle_positions: list, angle_velocities: list,
                      memory_blink_flags: Dict[str, int], memory_color: Tuple[int, int, int]):
        """Update the main display"""
        # Get fresh copy of current GUI image
        self.current_image = self.gui_images[self.state.current_gui].copy()
        
        # Update GUI-specific elements
        if self.state.current_gui == 1:
            self.update_gui1_display(self.current_image, current_angle, angle_positions)
        elif self.state.current_gui == 2:
            self.update_gui2_display(self.current_image, current_angle, angle_velocities)
        
        # Update button display for current gaze
        self.update_button_display(self.current_image, current_flags, self.colors['active'])
        
        # Handle blink visualization
        self.handle_blink_display(blink_flags, dbl_blink_gui, blink_time, stop_flag,
                                 memory_blink_flags, memory_color, current_flags)
    
    def handle_blink_display(self, blink_flags: Dict[str, int], dbl_blink_gui: int,
                           blink_time: float, stop_flag: int, memory_blink_flags: Dict[str, int],
                           memory_color: Tuple[int, int, int], current_flags: Dict[str, int]):
        """Handle blink-related display updates"""
        # Check if not in neutral zone
        if not (blink_flags['top'] and blink_flags['center']) and not (current_flags['top'] and current_flags['center']):
            # Determine blink display color and size
            if (time.time() - blink_time) < 99:
                if dbl_blink_gui == 0:
                    # First blink
                    color = self.colors['blink_first']
                    size_offset = 20
                elif dbl_blink_gui == 1 or stop_flag == 1:
                    # Second blink or stop
                    color = self.colors['blink_second']
                    size_offset = 20
                else:
                    color = self.colors['inactive']
                    size_offset = 20
                
                # Draw blink indication
                self.update_button_display_with_size(blink_flags, color, size_offset)
            else:
                # No active blink
                self.update_button_display_with_size(
                    {'top': 1, 'bot': 1, 'left': 1, 'center': 1, 'right': 1}, 
                    self.colors['inactive'], 20
                )
        else:
            # In neutral zone, show memory
            self.update_button_display_with_size(memory_blink_flags, memory_color, 20)
    
    def update_button_display_with_size(self, flags: Dict[str, int], 
                                       color: Tuple[int, int, int], size_offset: int):
        """Update button display with custom size"""
        h, w = self.current_image.shape[:2]
        bw = self.state.button_width + size_offset
        bh = self.state.button_height + size_offset
        d, offset = self.state.border_thickness, max(0, self.state.border_offset - size_offset//2)
        
        # Similar to update_button_display but with size modifications
        positions = {
            'left_top': (0+offset, bw, 0+offset, bh),
            'left_bottom': (0+offset, bw, h-bh, h-offset),
            'center_top': (int(w/2)-int(bw/2), int(w/2)+int(bw/2), 0+offset, bh),
            'center_bottom': (int(w/2)-int(bw/2), int(w/2)+int(bw/2), h-bh, h-offset),
            'right_top': (w-bw, w-offset, 0+offset, bh),
            'right_bottom': (w-bw, w-offset, h-bh, h-offset)
        }
        
        # Draw buttons based on flags
        for button_name, (x0, x1, y0, y1) in positions.items():
            should_draw = False
            
            if 'left_top' == button_name and flags.get('left') and flags.get('top'):
                should_draw = True
            elif 'left_bottom' == button_name and flags.get('left') and flags.get('bot'):
                should_draw = True
            elif 'center_top' == button_name and flags.get('center') and flags.get('top'):
                should_draw = True
            elif 'center_bottom' == button_name and flags.get('center') and flags.get('bot'):
                should_draw = True
            elif 'right_top' == button_name and flags.get('right') and flags.get('top'):
                should_draw = True
            elif 'right_bottom' == button_name and flags.get('right') and flags.get('bot'):
                should_draw = True
            elif flags.get('top') == 1 and flags.get('bot') == 1 and flags.get('left') == 1 and flags.get('center') == 1 and flags.get('right') == 1:
                # All buttons
                should_draw = True
            
            if should_draw:
                self.draw_button_border(self.current_image, x0, x1, y0, y1, d, color)
    
    def update_display_no_face(self):
        """Update display when no face is detected"""
        self.current_image = self.gui_images[self.state.current_gui].copy()
        # Show all buttons as inactive
        flags = {'top': 1, 'bot': 1, 'left': 1, 'center': 1, 'right': 1}
        self.update_button_display(self.current_image, flags, self.colors['inactive'])
    
    def handle_interactions(self, blink_flags: Dict[str, int], dbl_blink_gui: int, 
                          current_angle: int) -> Optional[Dict]:
        """Handle GUI interactions and return actions"""
        if not dbl_blink_gui:
            return None
        
        # GUI 1 interactions
        if self.state.current_gui == 1:
            return self.handle_gui1_interactions(blink_flags, current_angle)
        
        # GUI 2 interactions
        elif self.state.current_gui == 2:
            return self.handle_gui2_interactions(blink_flags, current_angle)
        
        # GUI 3 interactions
        elif self.state.current_gui == 3:
            return self.handle_gui3_interactions(blink_flags)
        
        return None
    
    def handle_gui1_interactions(self, blink_flags: Dict[str, int], current_angle: int) -> Optional[Dict]:
        """Handle GUI 1 specific interactions"""
        # Switch to GUI 2
        if blink_flags['bot'] and blink_flags['left']:
            self.state.current_gui = 2
            return {'type': 'switch_gui', 'target': 2}
        
        # Switch angle
        elif blink_flags['bot'] and blink_flags['center']:
            return {'type': 'switch_angle'}
        
        # Increase angle
        elif blink_flags['top'] and blink_flags['left']:
            return {'type': 'angle_inc'}
        
        # Decrease angle
        elif blink_flags['top'] and blink_flags['right']:
            return {'type': 'angle_dec'}
        
        # Stop
        elif blink_flags['bot'] and blink_flags['right']:
            return {'type': 'stop'}
        
        return None
    
    def handle_gui2_interactions(self, blink_flags: Dict[str, int], current_angle: int) -> Optional[Dict]:
        """Handle GUI 2 specific interactions"""
        # Switch to GUI 1
        if blink_flags['bot'] and blink_flags['left']:
            self.state.current_gui = 1
            return {'type': 'switch_gui', 'target': 1}
        
        # Switch to GUI 3
        elif blink_flags['bot'] and blink_flags['center']:
            self.state.current_gui = 3
            return {'type': 'switch_gui', 'target': 3}
        
        # Increase velocity
        elif blink_flags['top'] and blink_flags['left']:
            return {'type': 'velocity_inc'}
        
        # Decrease velocity
        elif blink_flags['top'] and blink_flags['right']:
            return {'type': 'velocity_dec'}
        
        # Stop
        elif blink_flags['bot'] and blink_flags['right']:
            return {'type': 'stop'}
        
        return None
    
    def handle_gui3_interactions(self, blink_flags: Dict[str, int]) -> Optional[Dict]:
        """Handle GUI 3 specific interactions"""
        # Switch to GUI 1
        if blink_flags['bot'] and blink_flags['left']:
            self.state.current_gui = 1
            return {'type': 'switch_gui', 'target': 1}
        
        # Stop
        elif blink_flags['bot'] and blink_flags['right']:
            return {'type': 'stop'}
        
        return None
    
    def render(self):
        """Render the current frame"""
        cv2.imshow("EyeTracker", self.current_image)
    
    def cleanup(self):
        """Clean up GUI resources"""
        cv2.destroyWindow("EyeTracker")
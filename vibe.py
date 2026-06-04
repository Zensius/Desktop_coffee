import tkinter as tk
import os
import random

class DesktopPet:
    def __init__(self):
        self.DEBUG_MODE = True  # Set to False to hide the green debug box
        
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        if self.DEBUG_MODE:
            self.bg_color = "#00FF00" 
            self.root.config(bg="red", bd=3, relief="solid") 
        else:
            self.bg_color = 'systemTransparent' if self.root.tk.call('tk', 'windowingsystem') == 'aqua' else '#111111'
            self.root.config(bg=self.bg_color)
            self.root.attributes('-transparentcolor', '#111111')

        # -------------------------------------------------------------
        # 1. EXPANDED ANIMATION FILES
        # -------------------------------------------------------------
        self.animation_files = {
            "idle": "personal/pet_idle.gif",
            "walk_left": "personal/pet_walk_left.gif",
            "walk_right": "personal/pet_walk_right.gif",
            "groom": "personal/pet_groom.gif",
            "look_around": "personal/pet_look.gif"
        }
        
        self.animations = {}
        self.load_all_animations()
        
        # Initial State
        self.current_state = "idle"
        self.current_frame = 0
        
        initial_image = self.animations[self.current_state][self.current_frame]
        self.label = tk.Label(self.root, image=initial_image, bg=self.bg_color)
        self.label.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # 2. SCREEN CONSTRAINTS & POSITIONING
        # -------------------------------------------------------------
        # Get actual screen dimensions dynamically
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # We need to wait a split second for Tkinter to draw the widget 
        # so we can accurately read the pet's pixel width.
        self.root.update_idletasks()
        self.pet_width = self.label.winfo_reqwidth()
        self.pet_height = self.label.winfo_reqheight()

        # Start near the bottom right of the screen (above the taskbar)
        self.x = self.screen_width // 2
        self.y = self.screen_height - self.pet_height - 60 
        self.root.geometry(f"+{self.x}+{self.y}")

        # Interaction / Brain variables
        self.is_interacting = False
        self.popup_window = None
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Mouse Bindings
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.drag_motion)
        self.label.bind("<ButtonRelease-1>", self.stop_drag)
        self.label.bind("<Button-3>", self.open_popup) 

        # Start loops
        self.update_animation()
        self.update_movement()
        
        # Kick off the random behavior brain!
        self.root.after(10000, self.pet_brain) 
        
        self.root.mainloop()

    def load_all_animations(self):
        for state_name, file_path in self.animation_files.items():
            self.animations[state_name] = []
            if not os.path.exists(file_path):
                print(f"Warning: {file_path} not found. Using 'idle' fallback.")
                continue

            frame_index = 0
            while True:
                try:
                    frame = tk.PhotoImage(file=file_path, format=f"gif -index {frame_index}")
                    self.animations[state_name].append(frame)
                    frame_index += 1
                except tk.TclError:
                    break
        
        # Fallback security: If any custom animation is missing, map it to 'idle'
        for state in self.animation_files.keys():
            if state not in self.animations or not self.animations[state]:
                if "idle" in self.animations and self.animations["idle"]:
                    self.animations[state] = self.animations["idle"]
                else:
                    raise RuntimeError("Critical Error: You must at least have a valid 'pet_idle.gif'!")

    def change_state(self, new_state):
        if new_state in self.animations and self.animations[new_state]:
            self.current_state = new_state
            self.current_frame = 0

    # -------------------------------------------------------------
    # 3. RANDOM BEHAVIOR BRAIN
    # -------------------------------------------------------------
    def pet_brain(self):
        """Dictates what the pet wants to do next based on probabilities."""
        # Only switch behaviors if the user isn't currently messing with it
        if not self.is_interacting:
            # List of possible random choices
            choices = ["idle", "walk_left", "walk_right", "groom", "look_around"]
            next_behavior = random.choice(choices)
            
            self.change_state(next_behavior)
            
        # How long should it stay in this behavior? (Pick a random time between 2 to 6 seconds)
        next_brain_tick = random.randint(10000, 30000)
        self.root.after(next_brain_tick, self.pet_brain)

    def update_animation(self):
        active_frames = self.animations[self.current_state]
        if active_frames:
            self.current_frame = (self.current_frame + 1) % len(active_frames)
            self.label.config(image=active_frames[self.current_frame])
            
        self.root.after(100, self.update_animation)

    # -------------------------------------------------------------
    # 4. CONSTRAINED MOVEMENT LOGIC
    # -------------------------------------------------------------
    def update_movement(self):
        if not self.is_interacting:
            # Move Left
            if self.current_state == "walk_left":
                self.x -= 1
                # If hit left screen border, force turn right
                if self.x < 0:
                    self.x = 0
                    self.change_state("walk_right")
            
            # Move Right
            elif self.current_state == "walk_right":
                self.x += 1
                # If hit right screen border (Screen Width minus Pet Width), force turn left
                if self.x > (self.screen_width - self.pet_width):
                    self.x = self.screen_width - self.pet_width
                    self.change_state("walk_left")

            self.root.geometry(f"+{self.x}+{self.y}")
        
        self.root.after(50, self.update_movement)

    # --- DRAG LOGIC ---
    def start_drag(self, event):
        self.is_interacting = True
        self.change_state("idle") 
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag_motion(self, event):
        # Allow dragging anywhere, but constrain it inside screen width limits
        calculated_x = self.root.winfo_x() + (event.x - self.drag_start_x)
        self.y = self.root.winfo_y() + (event.y - self.drag_start_y)
        
        # Clamp X position to screen bounds during a drag
        self.x = max(0, min(calculated_x, self.screen_width - self.pet_width))
        self.root.geometry(f"+{self.x}+{self.y}")

    def stop_drag(self, event):
        if not self.popup_window or not tk.Toplevel.winfo_exists(self.popup_window):
            self.is_interacting = False
            # Let the brain automatically decide what to do immediately upon dropping
            self.pet_brain()

    # --- POPUP LOGIC ---
    def open_popup(self, event):
        self.is_interacting = True
        self.change_state("look_around") # Looks at menu options

        if self.popup_window and tk.Toplevel.winfo_exists(self.popup_window):
            self.popup_window.focus_set()
            return

        self.popup_window = tk.Toplevel(self.root)
        self.popup_window.title("Pet Menu")
        self.popup_window.geometry("200x150")
        self.popup_window.geometry(f"+{self.x + self.pet_width + 10}+{self.y}")
        self.popup_window.attributes('-topmost', True)

        tk.Label(self.popup_window, text="What do you want to do?", font=("Arial", 12)).pack(pady=10)
        tk.Button(self.popup_window, text="Feed Pet", command=lambda: print("Nom nom nom")).pack(pady=5)
        tk.Button(self.popup_window, text="Close Menu", command=self.close_popup).pack(pady=5)

        self.popup_window.protocol("WM_DELETE_WINDOW", self.close_popup)

    def close_popup(self):
        if self.popup_window:
            self.popup_window.destroy()
            self.popup_window = None
        self.is_interacting = False
        self.pet_brain()

if __name__ == "__main__":
    DesktopPet()
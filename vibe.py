import tkinter as tk
import os
import random

class DesktopPet:
    def __init__(self):
        self.DEBUG_MODE = False  # Set to False to hide the green debug box
        
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
            "idle": "gif/pet_idle.gif",
            "idle2": "gif/pet_idle2.gif",
            "walk_left": "gif/pet_move_left.gif",
            "walk_right": "gif/pet_move_right.gif",
            "sleep": "gif/pet_sleep.gif",
            "sit": "gif/pet_sit.gif"
        }
        
        self.animations = {}
        self.load_all_animations()
        
        # Initial State
        self.current_state = "idle"
        self.current_frame = 0
        self.current_loop_count = 0  # Tracks how many times the animation has played
        self.target_loops = 1        # How many loops to play before changing behavior
        
        initial_image = self.animations[self.current_state][self.current_frame]
        self.label = tk.Label(self.root, image=initial_image, bg=self.bg_color)
        self.label.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # 2. SCREEN CONSTRAINTS & POSITIONING
        # -------------------------------------------------------------
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        self.root.update_idletasks()
        self.pet_width = self.label.winfo_reqwidth()
        self.pet_height = self.label.winfo_reqheight()

        self.x = self.screen_width // 3
        self.y = self.screen_height - self.pet_height - 30 
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
        
        # Kick off the first decision natively (No root.after timer needed anymore)
        self.pet_brain() 
        
        self.root.mainloop()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        import sys
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
    
    def load_all_animations(self):
        for state_name, relative_path in self.animation_files.items():
            self.animations[state_name] = []
            
            # --- UPDATE THIS LINE TO USE THE HELPER ---
            file_path = self.resource_path(relative_path)
            
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
    # 3. RANDOM BEHAVIOR BRAIN (Loop-Based)
    # -------------------------------------------------------------
    def pet_brain(self):
        """Decides the next behavior and how many times it will loop."""
        if not self.is_interacting:
            choices = ["sit", "idle", "idle2", "sleep", "walk_left", "walk_right"]
            next_behavior = random.choices(choices, weights=[7,1,1,1,3,3], k=1)[0]
            self.change_state(next_behavior)
            
            # Determine how many full animation cycles to perform before thinking again
            self.target_loops = random.randint(2, 6) 
            self.current_loop_count = 0
            
            # Notice there is no self.root.after() here anymore. 
            # The animation loop handles triggering the brain now.

    def update_animation(self):
        active_frames = self.animations[self.current_state]
        if active_frames:
            self.current_frame += 1
            
            # Check if the animation just finished a full loop
            if self.current_frame >= len(active_frames):
                self.current_frame = 0
                self.current_loop_count += 1
                
                # If we've hit our target loops, time for the brain to pick a new behavior
                if self.current_loop_count >= self.target_loops and not self.is_interacting:
                    self.pet_brain()
                    
            self.label.config(image=active_frames[self.current_frame])
            
        self.root.after(100, self.update_animation)

    # -------------------------------------------------------------
    # 4. CONSTRAINED MOVEMENT LOGIC
    # -------------------------------------------------------------
    def update_movement(self):
        if not self.is_interacting:
            if self.current_state == "walk_left":
                self.x -= 1
                if self.x < 0:
                    self.x = 0
                    self.change_state("walk_right")
            
            elif self.current_state == "walk_right":
                self.x += 1
                if self.x > (self.screen_width - self.pet_width):
                    self.x = self.screen_width - self.pet_width
                    self.change_state("walk_left")

            self.root.geometry(f"+{self.x}+{self.y}")
        
        self.root.after(50, self.update_movement)

    # --- DRAG LOGIC ---
    def start_drag(self, event):
        # We no longer force "idle" or set is_interacting. 
        # This lets the pet keep doing its current animation while you drag it.
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag_motion(self, event):
        calculated_x = self.root.winfo_x() + (event.x - self.drag_start_x)
        self.y = self.root.winfo_y() + (event.y - self.drag_start_y)
        
        self.x = max(0, min(calculated_x, self.screen_width - self.pet_width))
        self.root.geometry(f"+{self.x}+{self.y}")

    def stop_drag(self, event):
        # We completely removed the self.pet_brain() call here to stop the exponential timer bug.
        pass

    # --- POPUP LOGIC ---
    def open_popup(self, event):
        self.is_interacting = True
        self.change_state("idle") 

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

        tk.Button(self.popup_window, text="Exit Desktop Pet", command=self.root.destroy, fg="red").pack(pady=5)

        self.popup_window.protocol("WM_DELETE_WINDOW", self.close_popup)
    def close_popup(self):
        if self.popup_window:
            self.popup_window.destroy()
            self.popup_window = None
        self.is_interacting = False
        self.pet_brain()

if __name__ == "__main__":
    DesktopPet()

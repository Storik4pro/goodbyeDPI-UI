import tkinter as tk

class LoadingIndicator:
    def __init__(self, master, bg_color="#ffffff", fg_color="blue", width=400, height=5):
        self.master = master
        self.canvas_width = width
        self.canvas_height = height
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg=bg_color, highlightthickness=0)
        self.canvas.pack(fill="x", padx=(5, 10))
        self.min_bar_width = self.canvas_width // 5
        self.max_bar_width = self.canvas_width // 3
        self.bar_height = self.canvas_height
        self.bar = None
        self.position = -self.max_bar_width / 2  
        self.is_fast = False
        self.speed_slow = 12  
        self.speed_fast = 20 
        self.speed = self.speed_slow
        self.fg_color = fg_color
        self.animate()

    def animate(self):
        if self.bar:
            self.canvas.delete(self.bar)

        self.position += self.speed

        center_of_canvas = self.canvas_width / 2
        distance_from_center = abs(center_of_canvas - self.position)
        max_distance = center_of_canvas
        normalized_distance = distance_from_center / max_distance
        bar_width = self.min_bar_width + (self.max_bar_width - self.min_bar_width) * (1 - normalized_distance)

        left = self.position - bar_width / 2
        right = self.position + bar_width / 2

        self.bar = self.canvas.create_rectangle(left, 0, right, 0 + self.bar_height, fill=self.fg_color, outline='')

        if left > self.canvas_width:
            self.is_fast = not self.is_fast
            self.speed = self.speed_fast if self.is_fast else self.speed_slow
            self.position = -self.max_bar_width / 2 

        self.master.after(20, self.animate)
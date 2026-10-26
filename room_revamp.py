import tkinter as tk
from tkinter import messagebox, ttk


class RoomRevampApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RoomRevamp — Interior Design Assistant")
        self.root.geometry("1200x750")
        self.root.config(bg="#f4f4f9")

        # Room and Furniture Data
        self.room_length = 400  # cm
        self.room_width = 300  # cm
        self.placed_furniture = []  # List of dictionaries storing placed items

        # Drag-and-drop state variables
        self.dragging_index = None
        self.mouse_x = 0
        self.mouse_y = 0
        self.scale = 1.0

        # Predefined furniture catalog (Name -> Dimensions & Default Color)
        self.catalog = {
            "Bed": {"length": 200, "width": 150, "color": "#ffadad"},
            "Table": {"length": 120, "width": 60, "color": "#ffd6a5"},
            "Chair": {"length": 50, "width": 50, "color": "#fdffb6"},
            "Wardrobe": {"length": 100, "width": 60, "color": "#caffbf"},
            "Sofa": {"length": 180, "width": 80, "color": "#9bf6ff"}
        }

        # Build the user interface
        self.create_widgets()

    def create_widgets(self):
        # --- LEFT CONTROL PANEL ---
        control_frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief=tk.GROOVE)
        control_frame.place(x=20, y=20, width=380, height=710)

        tk.Label(control_frame, text="Room Setup", font=("Arial", 15, "bold"), bg="#ffffff").pack(pady=15)

        # Room Dimensions Inputs
        tk.Label(control_frame, text="Room Length (cm):", font=("Arial", 11), bg="#ffffff").pack(anchor="w", padx=20)
        self.entry_length = tk.Entry(control_frame, font=("Arial", 11))
        self.entry_length.insert(0, "400")
        self.entry_length.pack(fill="x", padx=20, pady=8)

        tk.Label(control_frame, text="Room Width (cm):", font=("Arial", 11), bg="#ffffff").pack(anchor="w", padx=20)
        self.entry_width = tk.Entry(control_frame, font=("Arial", 11))
        self.entry_width.insert(0, "300")
        self.entry_width.pack(fill="x", padx=20, pady=8)

        # Wall Color Dropdown
        tk.Label(control_frame, text="Wall Color:", font=("Arial", 11), bg="#ffffff").pack(anchor="w", padx=20)
        self.color_var = tk.StringVar(value="White")
        color_dropdown = ttk.Combobox(control_frame, textvariable=self.color_var,
                                      values=["White", "Beige", "Light Grey", "Soft Blue"], font=("Arial", 11))
        color_dropdown.pack(fill="x", padx=20, pady=8)

        tk.Button(control_frame, text="Create / Update Room", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                  command=self.create_room).pack(fill="x", padx=20, pady=12)

        ttk.Separator(control_frame, orient="horizontal").pack(fill="x", padx=20, pady=15)

        # Furniture Selection
        tk.Label(control_frame, text="Add Furniture", font=("Arial", 15, "bold"), bg="#ffffff").pack(pady=5)

        tk.Label(control_frame, text="Select Item:", font=("Arial", 11), bg="#ffffff").pack(anchor="w", padx=20)
        self.furniture_var = tk.StringVar(value="Bed")
        furniture_dropdown = ttk.Combobox(control_frame, textvariable=self.furniture_var,
                                          values=list(self.catalog.keys()), font=("Arial", 11))
        furniture_dropdown.pack(fill="x", padx=20, pady=8)

        # Action Buttons
        tk.Button(control_frame, text="Add to Room", bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                  command=self.add_furniture).pack(fill="x", padx=20, pady=6)
        tk.Button(control_frame, text="Check Overlap", bg="#FF9800", fg="white", font=("Arial", 11, "bold"),
                  command=self.check_overlap).pack(fill="x", padx=20, pady=6)
        tk.Button(control_frame, text="Calculate Space", bg="#9C27B0", fg="white", font=("Arial", 11, "bold"),
                  command=self.calculate_space).pack(fill="x", padx=20, pady=6)
        tk.Button(control_frame, text="Suggest Layout", bg="#00bcd4", fg="white", font=("Arial", 11, "bold"),
                  command=self.suggest_layout).pack(fill="x", padx=20, pady=6)
        tk.Button(control_frame, text="Reset Layout", bg="#f44336", fg="white", font=("Arial", 11, "bold"),
                  command=self.reset_layout).pack(fill="x", padx=20, pady=12)

        # --- RIGHT CANVAS AREA ---
        self.canvas = tk.Canvas(self.root, bg="white", bd=2, relief=tk.SOLID)
        self.canvas.place(x=420, y=20, width=750, height=500)

        # Bind mouse events for drag-and-drop
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # --- BOTTOM STATUS / OUTPUT PANEL ---
        self.status_label = tk.Label(self.root, text="Status: Room ready. Click and drag furniture items to move them!",
                                     font=("Arial", 12), bg="#f4f4f9", fg="#333", anchor="nw", justify="left", bd=2,
                                     relief=tk.GROOVE)
        self.status_label.place(x=420, y=535, width=750, height=195)

        # Initial render
        self.draw_room()

    def create_room(self):
        try:
            self.room_length = float(self.entry_length.get())
            self.room_width = float(self.entry_width.get())
            if self.room_length <= 0 or self.room_width <= 0:
                raise ValueError
            self.placed_furniture.clear()
            self.draw_room()
            self.status_label.config(text=f"Status: Room updated to {self.room_length}cm x {self.room_width}cm.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter positive numbers for room dimensions.")

    def draw_room(self):
        self.canvas.delete("all")

        color_map = {"White": "#ffffff", "Beige": "#f5f5dc", "Light Grey": "#e0e0e0", "Soft Blue": "#e6f2ff"}
        bg_color = color_map.get(self.color_var.get(), "#ffffff")

        canvas_w = 710
        canvas_h = 460

        self.scale = min(canvas_w / self.room_length, canvas_h / self.room_width)

        draw_origin_x = 20
        draw_origin_y = 20

        room_draw_w = self.room_length * self.scale
        room_draw_h = self.room_width * self.scale

        # Draw Room Boundary
        self.canvas.create_rectangle(
            draw_origin_x, draw_origin_y,
            draw_origin_x + room_draw_w, draw_origin_y + room_draw_h,
            fill=bg_color, outline="black", width=3
        )

        # Draw each placed furniture item with a unique tag corresponding to its index
        for i, item in enumerate(self.placed_furniture):
            fx = draw_origin_x + (item["x"] * self.scale)
            fy = draw_origin_y + (item["y"] * self.scale)
            fw = item["length"] * self.scale
            fh = item["width"] * self.scale

            # Create rectangle and text with item tags
            self.canvas.create_rectangle(fx, fy, fx + fw, fy + fh, fill=item["color"], outline="black", width=2,
                                         tags=("furniture", f"item_{i}"))
            self.canvas.create_text(fx + fw / 2, fy + fh / 2, text=item["name"], font=("Arial", 10, "bold"),
                                    tags=("furniture", f"item_{i}"))

    def add_furniture(self):
        selected_name = self.furniture_var.get()
        f_info = self.catalog[selected_name]

        offset = len(self.placed_furniture) * 35
        new_x = 20 + offset
        new_y = 20 + offset

        if new_x + f_info["length"] > self.room_length or new_y + f_info["width"] > self.room_width:
            new_x, new_y = 20, 20

        new_item = {
            "name": selected_name,
            "length": f_info["length"],
            "width": f_info["width"],
            "x": new_x,
            "y": new_y,
            "color": f_info["color"]
        }

        self.placed_furniture.append(new_item)
        self.draw_room()
        self.status_label.config(text=f"Status: Added {selected_name}. You can drag it anywhere inside the room!")

    # --- DRAG AND DROP EVENT HANDLERS ---
    def on_press(self, event):
        clicked = self.canvas.find_withtag("current")
        if clicked:
            tags = self.canvas.gettags(clicked[0])
            for tag in tags:
                if tag.startswith("item_"):
                    self.dragging_index = int(tag.split("_")[1])
                    self.mouse_x = event.x
                    self.mouse_y = event.y
                    return
        self.dragging_index = None

    def on_drag(self, event):
        if self.dragging_index is not None:
            dx = event.x - self.mouse_x
            dy = event.y - self.mouse_y
            self.mouse_x = event.x
            self.mouse_y = event.y

            # Move all canvas shapes sharing this item's tag smoothly
            self.canvas.move(f"item_{self.dragging_index}", dx, dy)

    def on_release(self, event):
        if self.dragging_index is not None:
            rect_id = None
            for item_id in self.canvas.find_withtag(f"item_{self.dragging_index}"):
                if self.canvas.type(item_id) == "rectangle":
                    rect_id = item_id
                    break

            if rect_id:
                coords = self.canvas.coords(rect_id)
                if coords:
                    cx1, cy1, cx2, cy2 = coords
                    draw_origin_x = 20
                    draw_origin_y = 20

                    # Convert pixel coordinates back to real room centimeters
                    new_x = (cx1 - draw_origin_x) / self.scale
                    new_y = (cy1 - draw_origin_y) / self.scale

                    item = self.placed_furniture[self.dragging_index]

                    # Enforce strict boundary validation
                    if new_x < 0: new_x = 0
                    if new_y < 0: new_y = 0
                    if new_x + item["length"] > self.room_length:
                        new_x = self.room_length - item["length"]
                    if new_y + item["width"] > self.room_width:
                        new_y = self.room_width - item["width"]

                    item["x"] = new_x
                    item["y"] = new_y

            self.dragging_index = None
            self.draw_room()  # Redraw to ensure correct alignment and labels
            self.status_label.config(text="Status: Furniture position updated.")

    def check_overlap(self):
        if len(self.placed_furniture) < 2:
            self.status_label.config(text="Status: Add at least 2 furniture items to check overlap.")
            return

        overlap_found = False
        for i in range(len(self.placed_furniture)):
            for j in range(i + 1, len(self.placed_furniture)):
                r1 = self.placed_furniture[i]
                r2 = self.placed_furniture[j]

                if not (r1["x"] + r1["length"] <= r2["x"] or
                        r1["x"] >= r2["x"] + r2["length"] or
                        r1["y"] + r1["width"] <= r2["y"] or
                        r1["y"] >= r2["y"] + r2["width"]):
                    overlap_found = True
                    self.status_label.config(text=f"WARNING: {r1['name']} and {r2['name']} overlap!")
                    return

        if not overlap_found:
            self.status_label.config(text="Status: No furniture overlaps detected. Good layout!")

    def calculate_space(self):
        room_area_m2 = (self.room_length * self.room_width) / 10000
        occupied_area_cm2 = sum(item["length"] * item["width"] for item in self.placed_furniture)
        occupied_area_m2 = occupied_area_cm2 / 10000
        available_area_m2 = room_area_m2 - occupied_area_m2

        if available_area_m2 < 0:
            available_area_m2 = 0

        info_text = (
            f"=== Space Calculation ===\n"
            f"• Total Room Area: {room_area_m2:.2f} m²\n"
            f"• Occupied Area: {occupied_area_m2:.2f} m²\n"
            f"• Available Floor Space: {available_area_m2:.2f} m²"
        )
        self.status_label.config(text=info_text)

    def suggest_layout(self):
        room_area = (self.room_length * self.room_width) / 10000
        occupied_area = sum(item["length"] * item["width"] for item in self.placed_furniture) / 10000

        if room_area == 0:
            return

        ratio = (occupied_area / room_area) * 100

        suggestion = f"=== Layout Suggestion ===\n"
        if ratio > 60:
            suggestion += "Room is overcrowded (>60% space used). Consider removing larger furniture."
        elif ratio < 20 and len(self.placed_furniture) > 0:
            suggestion += "Plenty of open space available! You can add more furniture items."
        else:
            suggestion += "Balanced room layout! Space utilization is optimal (20% - 60%)."

        self.status_label.config(text=suggestion)

    def reset_layout(self):
        self.placed_furniture.clear()
        self.draw_room()
        self.status_label.config(text="Status: Layout reset. Room cleared.")


if __name__ == "__main__":
    root = tk.Tk()
    app = RoomRevampApp(root)
    root.mainloop()
import tkinter as tk
from tkinter import filedialog, PhotoImage
from PIL import Image, ImageTk, ImageGrab, ImageFilter, ImageDraw
from pix2pix import generate_images
import tensorflow as tf

canvas_height = 550
canvas_width = 550
font_style = ("Heveltica", 12, 'bold')

class SketchToImageGenerator:
    def __init__(self, root):
        self.root = root  # Initialize the root (main window) for the GUI
        self.root.title("ArtiGen: Transfigure Images via Sketch-Guided Generative Model")  # Set the window title
        self.load_image  # Initialize the load_image method (missing parentheses)
        self.generated_image_photo = None  # Initialize the generated_image_photo variable to None

        # Input Section
        self.input_frame = tk.Frame(root)  # Create a frame for input widgets
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, rowspan=2)  # Set grid layout and padding
        self.input_frame.pack_propagate(False)  # Prevent input_frame from changing size

        # Input Image Label
        self.input_image_label = tk.Label(self.input_frame, text="Input Image", font=("Helvetica", 18, "bold"))
        self.input_image_label.grid(row=0, column=0, columnspan=3, pady=(5, 0))  # Set label properties

        # Pen Size Label
        self.pen_size_label = tk.Label(self.input_frame, text="Pen Size")  # Create a label for pen size
        self.pen_size_label.grid(row=1, column=0, pady=0, padx=(0, 0), sticky=tk.E,
                                 ipadx=10)  # Set label properties and position

        # Pen Size Variable
        self.pen_size_var = tk.DoubleVar()  # Create a DoubleVar to store pen size
        self.pen_size_var.set(0.1)  # Set the default pen size
        self.pen_size_entry = tk.Entry(self.input_frame, textvariable=self.pen_size_var,
                                       width=4)  # Create an entry widget for pen size
        self.pen_size_entry.grid(row=1, column=1, pady=5, padx=(0, 5), sticky=tk.W)  # Set entry properties and position

        # Pen Size Scale
        self.pen_size_scale = tk.Scale(self.input_frame, from_=0.1, to=10.0, orient=tk.HORIZONTAL,
                                       variable=self.pen_size_var,
                                       resolution=0.1, showvalue=False)  # Create a scale widget for pen size
        self.pen_size_scale.grid(row=1, column=1, pady=5, padx=(55, 0),
                                 sticky=tk.W)  # Set scale properties and position

        # Eraser Tick
        self.eraser_var = tk.BooleanVar()  # Create a BooleanVar to store eraser state
        self.eraser_var.set(False)  # Set the default eraser state to False
        self.eraser_button = tk.Checkbutton(self.input_frame, text="Eraser", variable=self.eraser_var,
                                            command=self.toggle_eraser)  # Create a checkbutton for eraser
        self.eraser_button.grid(row=1, column=1, pady=5, padx=(180, 0),
                                sticky=tk.W)  # Set checkbutton properties and position

        # Erase All Button (modified background color)
        self.erase_all_button = tk.Button(
            self.input_frame,
            text="Erase All",
            command=self.erase_all,
            font=font_style,
            bg="orange",  # Set background color
            activebackground="orange"  # Button background color when pressed
        )
        self.erase_all_button.grid(row=1, column=1, pady=5, padx=(260, 0), sticky=tk.W)

        # Undo Button (modified background color)
        self.undo_button = tk.Button(
            self.input_frame,
            text="Undo",
            command=self.undo_last,
            bg="gray",  # Set background color
            activebackground="lightgray",  # Button background color when pressed
            font = font_style
        )
        self.undo_button.grid(row=1, column=1, pady=5, padx=(350, 0), sticky=tk.W)

        # Sketch Canvas
        self.sketch_canvas = tk.Canvas(self.input_frame, bg="white", width=700,
                                       height=550)  # Create a canvas for sketching
        self.sketch_canvas.grid(row=2, column=0, columnspan=3, pady=10)  # Set canvas properties and position

        # Load Image Button (modified background color)
        self.load_button = tk.Button(
            self.input_frame,
            text="Load Image",
            command=self.load_image,
            compound="left",
            bg="white",
            fg="black",
            font=font_style,  # Create a button for loading an image
            anchor="center"  # Center the text on the button
        )
        self.load_button.grid(row=3, column=0, columnspan=3, pady=10)  # Center the button
        self.load_button.config(width=12, height=1, bg="blue")  # Set background color

        self.input_frame.pack_propagate(False)

        # Output Section
        self.output_frame = tk.Frame(root)  # Create a frame for output widgets
        self.output_frame.grid(row=0, column=1, padx=15, pady=10, rowspan=2)  # Set grid layout and padding

        # Generated Image Label
        self.generated_image_label = tk.Label(self.output_frame, text="Generated Image", font=("Helvetica", 18, "bold"))
        self.generated_image_label.grid(row=0, column=0, padx=10, pady=(5, 10), columnspan=200)  # Adjusted pady

        # Clear Output Button (modified background color)
        self.clear_output_button = tk.Button(
            self.output_frame,
            text="Clear Output",
            command=self.clear_output,  # Call clear_output method when clicked
            bg="orange",  # Set background color
            activebackground="orange",  # Button background color when pressed
            font=font_style
        )
        self.clear_output_button.grid(row=1, column=0, pady=(0, 1), padx=(300, 0),
                                      sticky=tk.W)  # Align with Erase All and Undo

        # Save Image Button (modified background color)
        self.save_image_button = tk.Button(
            self.output_frame,
            text="Save Image",
            command=self.save_image,
            bg="purple",  # Set background color
            fg="black",
            font=font_style
        )
        self.save_image_button.grid(row=3, column=0, pady=(10, 0), padx=(200, 0))

        # Generated Image Canvas
        self.generated_image_canvas = tk.Canvas(self.output_frame, bg="white", width=700,
                                                height=550)  # Create a canvas for displaying the generated image
        self.generated_image_canvas.grid(row=2, column=0, padx=10, pady=10,
                                         columnspan=2)  # Set canvas properties and position

        # Generate Image Button (modified background color)
        self.generate_button = tk.Button(
            root,
            text="Generate Image",
            command=self.generate_image,
            font=font_style,
            bg="green",  # Set background color
            fg="black",
            relief=tk.FLAT  # Create a button for generating images
        )
        self.generate_button.grid(row=2, column=0, columnspan=2, pady=10)  # Set button properties and position
        self.generate_button.config(width=15, height=1, bg="yellow")  # Set background color

        # Initialize drawing variables
        self.drawing = False
        self.last_x = None
        self.last_y = None
        self.drawn_objects = []  # List to store drawn objects for undo functionality

        # Bind mouse events for drawing
        self.sketch_canvas.bind("<B1-Motion>", self.draw)
        self.sketch_canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.sketch_canvas.bind("<ButtonRelease-1>", self.stop_drawing)

        # Input Frame Row Configuration
        self.input_frame.rowconfigure(0, weight=1)  # Make the row expandable

        # Output Frame Row Configuration
        self.output_frame.rowconfigure(0, weight=1)  # Make the row expandable

    def load_image(self):
        # Open a file dialog to select an image file
        file_path = tk.filedialog.askopenfilename(
            title="Load Sketch",
            filetypes=[("Image files", (".png", ".jpg", ".jpeg", ".gif"))]
        )
        if file_path:
            # Clear the input field (canvas) before loading a new image
            self.sketch_canvas.delete("all")

            image = Image.open(file_path)

            # Convert the image to Tkinter PhotoImage
            tk_image = ImageTk.PhotoImage(image)
            image_width = tk_image.width()
            image_height = tk_image.height()

            posX = (canvas_width - image_width) // 2
            posY = (canvas_height - image_height) // 2

            # posX, posY = 0, 0
            # Create an image on the canvas
            self.sketch_canvas.create_image(posX, posY, anchor=tk.NW, image=tk_image)

            # Keep a reference to avoid garbage collection
            self.sketch_canvas.image = tk_image

    def erase_all(self):
        # Clear the canvas when "Erase All" button is clicked
        self.sketch_canvas.delete("all")
        # Enable drawing after erasing all
        self.drawing = True

    def undo_last(self):
        print("Undoing last operation...")
        num_objects_to_delete = min(self.last_draw_count, len(self.drawn_objects))
        for _ in range(num_objects_to_delete):
            obj = self.drawn_objects.pop()  # Remove the ID of the last drawn object from the list
            # print("Deleted object:", obj)
            self.sketch_canvas.delete(obj)  # Delete the object from the canvas
        # print(f"Last {num_objects_to_delete} operations undone.")

    def draw(self, event):
        if self.drawing:
            x, y = event.x, event.y

            if self.last_x is not None and self.last_y is not None:
                size = int(self.pen_size_var.get())
                color = "black"

                # Check if eraser mode is activated
                if self.eraser_var.get():
                    size = int(self.pen_size_var.get())  # Use eraser size
                    color = "white"  # Eraser color

                # Draw a line on the canvas
                drawn_object = self.sketch_canvas.create_line(self.last_x, self.last_y, x, y, width=size, fill=color,
                                                              capstyle=tk.ROUND, smooth=tk.TRUE)
                self.drawn_objects.append(drawn_object)  # Add the drawn object to the list
                # print("Drawn object:", drawn_object)

                # Increment the draw count for this interaction
                self.draw_count += 1

            # Update the last coordinates for continuous drawing
            self.last_x = x
            self.last_y = y

    def start_drawing(self, event):
        # Set the drawing state to True when the mouse button is pressed
        self.drawing = True
        # Record the starting coordinates of the drawing
        self.last_x = event.x
        self.last_y = event.y
        # Initialize the count for this drawing interaction
        self.draw_count = 0

    def stop_drawing(self, event):
        # Set the drawing state to False when the mouse button is released
        self.drawing = False
        # Reset the last coordinates to None after drawing is stopped
        self.last_x = None
        self.last_y = None
        # Store the draw count for this interaction
        self.last_draw_count = self.draw_count

    def toggle_eraser(self):
        # Toggle between drawing and erasing modes
        if self.eraser_var.get():
            # Switch to eraser mode
            pen_size_value = abs(self.pen_size_var.get())
            self.last_pen_size = pen_size_value  # Store the last pen size
            self.pen_size_var.set(-pen_size_value)
            self.pen_size_label.config(text="Eraser Size")
            # Set the eraser scale to the absolute value of the pen scale
            self.pen_size_scale.set(pen_size_value)
        else:
            # Switch to pen mode
            if hasattr(self, 'last_pen_size'):
                # Use the last pen size if available
                self.pen_size_var.set(self.last_pen_size)
            else:
                # Default pen size if no last pen size is available
                self.pen_size_var.set(3.0)
            self.pen_size_label.config(text="Pen Size")
            # Set the pen scale to the absolute value of the eraser scale
            self.pen_size_scale.set(abs(self.pen_size_var.get()))

    def show_generated_image(self, generated_image):
        self.generated_image_canvas.delete("all")

        edge = (generated_image * 0.5 + 0.5) * 255.0
        edge = tf.cast(edge, dtype=tf.uint8)
        edge = edge.numpy()
        pil_image = Image.fromarray(edge)

        # Calculate the desired width and height for displaying the image
        desired_width = 400  # Adjust as needed
        desired_height = 400  # Adjust as needed

        # Resize the PIL Image to the desired size
        pil_image_resized = pil_image.resize((desired_width, desired_height), Image.LANCZOS)

        # Convert the resized PIL Image to a Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(pil_image_resized)

        # Calculate center position for the image on the canvas
        posX = (700 - desired_width) // 2
        posY = (550 - desired_height) // 2

        # Display the Tkinter PhotoImage on the Canvas
        self.generated_image_canvas.create_image(posX, posY, anchor=tk.NW, image=tk_image)

        # Keep a reference to avoid garbage collection
        self.generated_image_canvas.image = tk_image

    def generate_image(self):
        # Get the bounding box of the canvas
        x, y, width, height = self.sketch_canvas.bbox("all")

        # Capture the canvas content
        image = ImageGrab.grab(bbox=(self.sketch_canvas.winfo_rootx() + x,
                                     self.sketch_canvas.winfo_rooty() + y,
                                     self.sketch_canvas.winfo_rootx() + x + width,
                                     self.sketch_canvas.winfo_rooty() + y + height))

        # Resize the image to 256x256
        resized_image = image.resize((256, 256), Image.LANCZOS)
        save_path = "generated_image.png"
        resized_image.save(save_path)

        # Convert the resized image to a TensorFlow tensor with dtype=tf.uint8
        image_array = tf.image.convert_image_dtype(resized_image, dtype=tf.uint8)

        # Call the function with the tensorized image
        imtshowop = generate_images(image_array)

        # Display the generated image on the canvas
        self.show_generated_image(imtshowop)

        # Update the generated image attribute with the actual generated image
        self.generated_image = imtshowop

    def save_image(self):
        # Check if a generated image exists
        if hasattr(self, 'generated_image'):
            # Open a file dialog to specify the save location and file type
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"),
                                                                ("All files", ".")])
            if file_path:
                # Preprocess the generated image
                edge = (self.generated_image * 0.5 + 0.5) * 255.0
                edge = tf.cast(edge, dtype=tf.uint8)
                edge = edge.numpy()

                # Convert NumPy array to PIL image
                pil_image = Image.fromarray(edge)

                # Save the PIL image
                pil_image.save(file_path)

                print(f"Image saved to {file_path}")
            else:
                print("Save operation canceled.")
        else:
            print("No generated image to save.")

    def clear_output(self):
        # Clear the generated image canvas when "Clear Output" button is clicked
        self.generated_image_canvas.delete("all")


if __name__ == "__main__":
    # Create a Tkinter root window
    root = tk.Tk()

    # Create an instance of the SketchToImageGenerator class
    app = SketchToImageGenerator(root)

    # Allow the window to be displayed before entering the main loop
    root.update_idletasks()
    root.deiconify()

    # Start the Tkinter event loop
    root.mainloop()

import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk

def load_size(image_path, width, height):
    # This function should load an image and resize it to the given width and height
    # You need to implement this function to suit your needs
    image = Image.open(image_path)
    image = image.resize((width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(image)

class CallWindow:
    def __init__(self, root):
        self.root = root
        self.init_panel_create_ring_receiving()

    def init_panel_create_ring_receiving(self):
        self.root.geometry("600x400")
        self.root.configure(bg='#2f2f2f')

        # Label for "calling..." text
        self.calling_label = tk.Label(self.root, text="calling...", font=("Garet", 24), bg='#2f2f2f', fg='white')
        self.calling_label.pack(pady=40)

        # Load and place the image



        
        try:
            photo = load_size(r"..\images\ring1.png", 200, 200)  # Adjust the size as needed
        except Exception as e:
            print(f"Error loading image: {e}")
            photo = None

        if photo:
            self.image_label = tk.Label(self.root, image=photo, bg='#2f2f2f')
            self.image_label.image = photo  # Keep a reference to avoid garbage collection
            self.image_label.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    app = CallWindow(root)
    root.mainloop()

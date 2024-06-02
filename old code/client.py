from tkinter import *
from PIL import Image, ImageTk
import os

class Cli:
    def __init__(self, my_port, your_port):
        self.root = Tk()
        self.root.geometry("600x400")
        self.root.title("Home Page")
        self.images = {}

        # Initialize images and register panel
        self.init_images_dict()
        self.init_register_panel()

    def load_image(self, path, size=None):
        try:
            image = Image.open(path)
            if size:
                image = image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except FileNotFoundError:
            print(f"File not found: {path}")
            return None

    def init_images_dict(self):
        # נתיבים לתמונות
        main_image_path = r"..\images\logo VOW1.png"
        register_button_image_path = r"..\images\register icon1.png"
        login_button_image_path = r"..\images\log in icon1.png"

        # טעינת התמונות ושמירתם במילון
        self.images['main_image'] = self.load_image(main_image_path, (250, 224))
        self.images['register_button_image'] = self.load_image(register_button_image_path)
        self.images['login_button_image'] = self.load_image(login_button_image_path)

        # בדיקה אם התמונות נטענו בהצלחה
        for key, image in self.images.items():
            if image is None:
                print(f"Error loading image: {key}")

    def init_register_panel(self):
        # יצירת מסגרת עבור הכפתורים
        self.button_frame = Frame(self.root)
        self.button_frame.pack(pady=10)  # הצבת המסגרת עם מרווח מתחת

        # יצירת כפתורים והצבתם במסגרת, הסתרת המסגרת כך שהתמונות יראו כחלק מהמסך
        if 'register_button_image' in self.images:
            self.button_register = Button(self.button_frame, image=self.images['register_button_image'],
                                          command=self.submit_register, bd=0)
            self.button_register.pack(side=LEFT, padx=10)  # הצבת הכפתור הראשון עם מרווח מימין
        else:
            print("register_button_image not found in images dictionary")

        if 'login_button_image' in self.images:
            self.button_assign = Button(self.button_frame, image=self.images['login_button_image'],
                                        command=self.submit_register, bd=0)
            self.button_assign.pack(side=LEFT, padx=10)  # הצבת הכפתור השני עם מרווח מימין
        else:
            print("login_button_image not found in images dictionary")

    def submit_register(self):
        pass

    def main_loop(self):
        self.root.mainloop()

def Main():
    my_port = 2001
    your_port = 2002
    myclient = Cli(my_port, your_port)
    myclient.main_loop()

if __name__ == "__main__":
    Main()

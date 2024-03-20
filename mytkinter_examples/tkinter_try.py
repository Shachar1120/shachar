from tkinter import *
from tkinter.ttk import *


class A:
    def __init__(self):
        self.root = Tk()

        # sets the geometry of main
        # root window
        self.root.geometry("300x300")
        self.root.title("sign in")
        self.label = Label(self.root,
                      text="This is the main window")

        self.label.pack(pady=10)
        # Create a Button
        self.btn = Button(self.root, text='Click me !',
                     command=self.openNewWindow)

        self.btn.pack()

    def main_loop(self):
        self.root.mainloop()
    def click_button(self):
        # printing what happens when button pressed in python
        print("you pressed the button")


    # function to open a new window
    # on a button click
    def openNewWindow(self):
        self.btn.destroy()
        self.label.destroy()


        # sets the title of the
        # Toplevel widget
        self.root.title("call list")

        # sets the geometry of toplevel
        self.root.geometry("500x500")

        # A Label widget to show in toplevel
        self.label = Label(self.root,
              text="This is a new window").pack()

def Main():
    a = A()

    a.main_loop()

if __name__ == "__main__":
    Main()
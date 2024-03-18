# importing only those functions
# which are needed
from tkinter import *
from tkinter.ttk import *

# creating tkinter window
root = Tk()

# Adding widgets to the root window
Label(root, text='Hello', font=(
    'Verdana', 15)).pack(side=TOP, pady=10)

# Creating a photoimage object to use image
photo = PhotoImage(file=r"C:\שחר\tkinter\donotpress.gif")

# Create a Button
#btn = Button(root, text='Click me !', bd='5',
             #command=root.destroy)

# here, image option is used to
# set image on button
Button(root, text='Click Me !', image=photo, command=root.destroy).pack(side=TOP)

mainloop()
from tkinter import *
from tkinter.ttk import *
root = Tk()

photo = PhotoImage(file=r"C:\שחר\tkinter\ringing1.png")
photoimage = photo.subsample(3, 3)
btn_calling = Button(root, image=photoimage)
btn_calling.place(x=30, y=100)

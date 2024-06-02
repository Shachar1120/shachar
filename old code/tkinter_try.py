from pathlib import Path
from tkinter import Tk, Canvas, PhotoImage


window = Tk()

window.geometry("1280x720")
window.configure(bg="#161616")

canvas = Canvas(
    window,
    bg="#161616",
    height=875,
    width=1400,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)

canvas.place(x=0, y=0)
canvas.create_rectangle(
    0.0,
    783.0,
    1400.0,
    875.0,
    fill="#3D3D3D",
    outline="")

canvas.create_rectangle(
    0.0,
    0.0,
    1400.0,
    43.0,
    fill="#7D7D7D",
    outline="")

canvas.create_text(
    22.0,
    11.0,
    anchor="nw",
    text="Add your creative page title here :)",
    fill="#FFFFFF",
    font=("Inter Bold", 20 * -1)
)

window.mainloop()

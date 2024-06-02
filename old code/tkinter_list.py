import tkinter as tk

def item_clicked(item):
    print(f"Clicked item: {item}")

root = tk.Tk()
root.title("Clickable List")

# רשימת הפריטים
items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]

# יצירת כפתורים לכל פריט ברשימה
for item in items:
    button = tk.Button(root, text=item, command=lambda i=item: item_clicked(i), bd=0, relief="flat", bg=root.cget("bg"))
    button.pack(pady=5, padx=10, fill="x")

root.mainloop()
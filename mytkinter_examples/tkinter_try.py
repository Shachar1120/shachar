from tkinter import *
from tkinter.ttk import *


class A:
    def __init__(self):
        self.root = Tk()

        # sets the geometry of main
        # root window
        self.root.geometry("300x300")
        self.root.title("Register or Log in")
        self.label = Label(self.root,
                      text="Welcome to VidPal!")

        self.label.pack(pady=10)
        # Create a Button
        self.btn_reg = Button(self.root, text='Register', command=self.Register_Window)
        #self.btn_reg.pack(side=LEFT)
        self.btn_reg.place(x=30, y=100)


        # Create a Button
        self.btn_assign = Button(self.root, text='Log In', command=self.Assign_Window)
        #self.btn_reg.pack(side=RIGHT)
        self.btn_assign.place(x=200, y=100)

    def main_loop(self):
        self.root.mainloop()

    def Register_Window(self):
        # Toplevel object which will
        # be treated as a new window
        newWindow = Toplevel(self.root)

        # sets the title of the
        # Toplevel widget
        newWindow.title("New Window")

        # sets the geometry of toplevel
        newWindow.geometry("450x300")

        # the label for user_name
        self.user_name = Label(newWindow,text="Username")
        self.user_name.place(x=40,y=60)

        # the label for user_password
        self.user_password = Label(newWindow,text="Password")
        self.user_password.place(x=40, y=100)

        self.submit_button = Button(newWindow,text="Submit", command = lambda: self.Register_succeeded(newWindow))
        self.submit_button.place(x=40, y=130)

        self.user_name_input_area = Entry(newWindow,width=30)
        self.user_name_input_area.place(x=110, y=60)

        self.user_password_entry_area = Entry(newWindow, width=30)
        self.user_password_entry_area.place(x=110, y=100)


    def Register_succeeded(self, newWindow):
        # Destroy the widgets in the registration window
        self.user_name.destroy()
        self.user_password.destroy()
        self.submit_button.destroy()
        self.user_name_input_area.destroy()
        self.user_password_entry_area.destroy()

        # Create a label indicating successful registration
        Label(newWindow, text="Registration succeeded").pack()

        # Create a button to close the window
        Button(newWindow, text="Close", command=newWindow.destroy).pack()

    def Register_not_succeeded(self, newWindow):
        # Destroy the widgets in the registration window
        self.user_name.destroy()
        self.user_password.destroy()
        self.submit_button.destroy()
        self.user_name_input_area.destroy()
        self.user_password_entry_area.destroy()

        # Create a label indicating successful registration
        Label(newWindow, text="Couldn't register, Try Again!").pack()

        # Create a button to close the window
        Button(newWindow, text="Close", command=newWindow.destroy).pack()



    def Assign_Window(self):
        # Toplevel object which will
        # be treated as a new window
        newWindow = Toplevel(self.root)

        # sets the title of the
        # Toplevel widget
        newWindow.title("New Window")

        # sets the geometry of toplevel
        newWindow.geometry("450x300")

        # the label for user_name
        self.user_name = Label(newWindow, text="Username")
        self.user_name.place(x=40, y=60)

        # the label for user_password
        self.user_password = Label(newWindow, text="Password")
        self.user_password.place(x=40, y=100)

        self.submit_button = Button(newWindow, text="Submit", command=lambda: self.Assign_succeeded(newWindow))
        self.submit_button.place(x=40, y=130)

        self.user_name_input_area = Entry(newWindow, width=30)
        self.user_name_input_area.place(x=110, y=60)

        self.user_password_entry_area = Entry(newWindow, width=30)
        self.user_password_entry_area.place(x=110, y=100)



    def Assign_succeeded(self, newWindow):
        # Destroy the widgets in the log in window
        self.user_name.destroy()
        self.user_password.destroy()
        self.submit_button.destroy()
        self.user_name_input_area.destroy()
        self.user_password_entry_area.destroy()

        # Create a label indicating successful registration
        Label(newWindow, text="You Logged In successfuly!").pack()

        # Create a button to close the window
        Button(newWindow, text="Close", command=newWindow.destroy).pack()


    def Assign_not_succeeded(self, newWindow):
        # Destroy the widgets in the log in window
        self.user_name.destroy()
        self.user_password.destroy()
        self.submit_button.destroy()
        self.user_name_input_area.destroy()
        self.user_password_entry_area.destroy()

        # Create a label indicating successful registration
        Label(newWindow, text="Couldn't Log In, Try Again!").pack()

        # Create a button to close the window
        Button(newWindow, text="Close", command=newWindow.destroy).pack()


def Main():
    a = A()

    a.main_loop()

if __name__ == "__main__":
    Main()

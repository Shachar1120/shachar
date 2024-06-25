import threading
from tkinter import *
import tkinter.ttk as ttk
from PIL import Image, ImageTk  # ייבוא Image ו-ImageTk מ-Pillow

import socket
import pickle
from new_protocol import Pro

class RegisterPanel:
    def __init__(self, root, socket_to_server, complete_func, my_port):
        self.root = root
        self.panel_window = None
        self.socket_to_server = socket_to_server
        self.complete_func = complete_func
        self.my_port = my_port
        self.user1 = None

        self.images = {}


    def handle_response_Register(self, response):
        if response == Pro.cmds[Pro.REGISTER_NACK]:
            print("Maybe user already exist!!! try different username")
            return False
        elif response == Pro.cmds[Pro.REGISTER_ACK]:
            print("Registration succeedded")
            return True
        elif response == Pro.cmds[Pro.ASSIGN_NACK]:
            # they need to enter username and password again
            print("you need to enter password again")
            return False
            pass
        elif response == Pro.cmds[Pro.ASSIGN_ACK]:
            # add user to dift of assigned
            # create a token
            pass



    def load_image(self, path, size=None):
        # פונקציה לטעינת תמונה והמרתה לפורמט Tkinter
        image = Image.open(path)
        if size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)



    def submit_register(self):

        # hasattr is a python function that checks if a value exists
        if hasattr(self, 'try_again_label'):
            self.try_again_label.destroy()

        if hasattr(self, 'try_again_label1'):
            self.try_again_label.destroy()

        if hasattr(self, 'already_registered_try_again'):
            self.already_registered_try_again.destroy()

        # Create a label indicating successful registration
        cmd = "REGISTER"
        username = self.user_name_input_area.get()
        self.user1 = username
        password = self.user_password_entry_area.get()
        my_port = str(self.my_port)


        # Check if username and password are not empty
        if username.strip() and password.strip():
            print("the params:", username, password)

            params = [username.encode(), password.encode(), my_port.encode()]
            if not Pro.check_cmd_and_params(cmd, params):
                # Register not succeeded!!
                self.try_again_label1 = Label(self.register_panel_window, text="Couldn't Register! Try Again.")
                self.try_again_label1.pack()



            else:
                # send cmd and params(username, password) to server

                msg_to_send = Pro.create_msg(cmd.encode(), params)
                self.socket_to_server.send(msg_to_send)
                # get response from server
                res_response, msg_response = Pro.get_msg(self.socket_to_server)
                msg_response = msg_response
                if res_response:
                    opcode, nof_params, params = Pro.split_message(msg_response)

                    # res_response = False: only got cmd (like in REGISTER N/ACK, ASSIGN N/ACK)
                    if (opcode == "REGISTER_NACK") or (opcode == "REGISTER_ACK"):
                        print("cmd is register")
                        response = self.handle_response_Register(opcode)

                        if not response:  # if false = REGISTER_NACK
                            # checking if the lable already exists
                            if not hasattr(self, 'already_registered_try_again'):
                                self.already_registered_try_again = Label(self.register_panel_window,
                                                                          text="User Already Registered! Try To Log In / Use Differente Username")
                                self.already_registered_try_again.pack()

                            print(
                                "couldn't register (client already registered)")  # couldn't register/ client exists
                            print("continue to assign")
                            # client already exists! we need to continue to assign too
                            pass
                        else:
                            self.complete_func() #RegisterComplete function in Cli class
                            print("you registered successfully")


                            pass

        else:
            self.try_again_label = Label(self.register_panel_window, text="Username or password are empty! Try again.")
            self.try_again_label.pack()


    def init_panel_create(self):

        self.register_panel_window = self.root

        # Define font sizes and colors
        label_font = ("Garet", 14, "bold")
        entry_font = ("Arial", 12)
        label_color = "#5271FF"  # New blue color

        # Paths to images
        submit_button_image_path = r"..\images\submit.png"

        # Load the submit button image
        self.images['submit_button_image'] = self.load_image(submit_button_image_path)

        self.register_panel_window.title("Register")

        # Create labels with larger font size and new blue color
        self.user_name = Label(self.register_panel_window, text="Username", font=label_font, fg=label_color)
        self.user_name.place(x=40, y=60)

        self.user_password = Label(self.register_panel_window, text="Password", font=label_font, fg=label_color)
        self.user_password.place(x=40, y=100)

        # Create entry fields with larger font size
        self.user_name_input_area = Entry(self.register_panel_window, width=30, font=entry_font)
        self.user_name_input_area.place(x=160, y=60)

        self.user_password_entry_area = Entry(self.register_panel_window, width=30, font=entry_font)
        self.user_password_entry_area.place(x=160, y=100)

        # Create the submit button with an image and adjust its position
        self.submit_button = Button(self.register_panel_window, image=self.images['submit_button_image'], command=self.submit_register,
                                    bd=0)
        self.submit_button.place(x=170, y=140)  # Adjusted position 


    def init_panel_destroy(self):
        self.submit_button.destroy()
        self.user_password_entry_area.destroy()
        self.user_name_input_area.destroy()
        self.user_password.destroy()
        self.user_name.destroy()
        if hasattr(self, 'try_again_label') and self.try_again_label1:
            # Assign not succeeded!!
            self.try_again_label1 = None
            self.try_again_label1.pack()

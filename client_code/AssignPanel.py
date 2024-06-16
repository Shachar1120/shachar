import threading
from tkinter import *
import tkinter.ttk as ttk
from PIL import Image, ImageTk  # ייבוא Image ו-ImageTk מ-Pillow

import socket
import pickle
from new_protocol import Pro
import select
from time import time
from pathlib import Path
import pyaudio

class AssignPanel:
    def __init__(self, root, socket_to_server, complete_func):

        self.root = root
        self.panel_window = None
        self.socket_to_server = socket_to_server
        self.complete_func = complete_func
        self.assign_response = None

        self.images = {}


    def handle_assign_response(self, msg):
        opcode, nof_params, params = Pro.split_message(msg)
        if opcode == "ASSIGN_ACK":
            return True
        else:
            return False

    def load_image(self, path, size=None):
        image = Image.open(path)
        if size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def init_panel_create(self):

        self.assign_panel_window = self.root

        # Define font sizes and colors
        label_font = ("Garet", 14, "bold")
        entry_font = ("Arial", 12)
        label_color = "#5271FF"  # New blue color

        # Paths to images
        submit_button_image_path = r"..\images\submit.png"

        # Load the submit button image
        self.images['submit_button_image'] = self.load_image(submit_button_image_path)

        self.assign_panel_window.title("Log In")

        # Create labels with larger font size and new blue color
        self.user_name = Label(self.assign_panel_window, text="Username", font=label_font, fg=label_color)
        self.user_name.place(x=40, y=60)

        self.user_password = Label(self.assign_panel_window, text="Password", font=label_font, fg=label_color)
        self.user_password.place(x=40, y=100)

        # Create entry fields with larger font size
        self.user_name_input_area = Entry(self.assign_panel_window, width=30, font=entry_font)
        self.user_name_input_area.place(x=160, y=60)

        self.user_password_entry_area = Entry(self.assign_panel_window, width=30, font=entry_font)
        self.user_password_entry_area.place(x=160, y=100)

        # Create the submit button with an image and adjust its position
        self.submit_button = Button(self.assign_panel_window, image=self.images['submit_button_image'],
                                    command=self.submit_assign,
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



    def submit_assign(self):

        # hasattr is a python function that checks if a value exists
        cmd = "ASSIGN"
        username = self.user_name_input_area.get()
        password = self.user_password_entry_area.get()

        # Check if username and password are not empty
        if username.strip() and password.strip():
            print("the params:", username, password)

            params = [username.encode(), password.encode()]
            if not Pro.check_cmd_and_params(cmd, params):
                if not hasattr(self, 'try_again_label') or not self.try_again_label1:
                    # Assign not succeeded!!
                    self.try_again_label1 = Label(self.assign_panel_window, text="Couldn't Log In! Try Again.")
                    self.try_again_label1.pack()

            else:
                # send cmd and params(username, password) to server
                msg_to_send = Pro.create_msg(cmd.encode(), params)
                self.socket_to_server.send(msg_to_send)



                # get response from server
                res_response, msg_response = Pro.get_msg(self.socket_to_server)
                if res_response:
                    opcode, nof_params, params = Pro.split_message(msg_response)
                    if opcode == "ASSIGN_ACK":
                        print("this is the response!!", msg_response)
                        # only if register Ack- user is assigned!!
                        #moving into Logged In panel
                        self.complete_func() #AssignComplete function in Cli class

                    else:
                        if msg_response == "ASSIGN_NACK":
                            print("password is incorrect???")
                        # else another error


        else:
            self.try_again_label = Label(self.assign_panel_window, text="Username or password are empty! Try again.")
            self.try_again_label.pack()


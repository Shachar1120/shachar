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

    def handle_response_assign(self, response):
        # כנראה שלא משתמשת בפונקציה!!
        if response == "ASSIGN_NACK":
            # they need to enter username and password again
            print("you need to enter password again")
            return False
        elif response == "ASSIGN_ACK":
            return True


    def send_cmd(self, cmd: bytes, params):
        msg_to_send = Pro.create_msg(cmd, params)
        self.socket_to_server.send(msg_to_send)

    def check_if_pickle(self, msg):
        # כנראה שלא משתמשת בפונקציה!!
        try:
            # Try to unpickle the message
            pickle.loads(msg)
            # If successful, the message is in pickle format
            return True
        except pickle.UnpicklingError:
            # If unsuccessful, the message is not in pickle format
            return False

    # def split_message(self, message):
    #     message_parts = message.split(Pro.PARAMETERS_DELIMITER.encode())  # message: cmd + len(params) + params
    #     opcode = message_parts[0].decode()
    #     nof_params = int(message_parts[1].decode())
    #     params = message_parts[2:]
    #     return opcode, nof_params, params

    def handle_response_call_target(self, response):
        # כנראה שלא משתמשת בפונקציה!!
        if response == "TARGET_NACK":
            # they need to call another client
            print("the person you wanted to call to isn't assigned yet")
            print("call another person(from contacts)")
            return False
        elif response == "TARGET_ACK":
            return True

    def handle_cmd(self, cmd):
        # כנראה שלא משתמשת בפונקציה!!
        tof = Pro.check_cmd(cmd)
        if tof:
            # sending to server
            sending_cmd = Pro.create_msg(cmd.encode(), [])
            self.socket_to_server.send(sending_cmd)

            # receiving from server
            # self.handle_server_response(cmd, None)
            # if cmd == 'EXIT':
            #    return False
        # else:
        # print("Not a valid command, or missing parameters\n")

        return True


    def handle_assign_response(self, msg):
        msg_parts = msg.split(Pro.PARAMETERS_DELIMITER)
        print(msg_parts[0], "," , msg_parts[1])
        if msg_parts[0] == "ASSIGN_ACK":
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
        # # before class it was Assign_Window function!!!
        # # Toplevel object which will
        # # be treated as a new window
        #
        # self.assign_panel_window = self.root
        # # sets the title of the
        # self.assign_panel_window.title("Log In")
        #
        # # sets the geometry of toplevel
        # self.assign_panel_window.geometry("600x400")
        #
        # # the label for user_name
        # self.user_name = Label(self.assign_panel_window, text="Username")
        # self.user_name.place(x=40, y=60)
        #
        # # the label for user_password
        # self.user_password = Label(self.assign_panel_window, text="Password")
        # self.user_password.place(x=40, y=100)
        #
        # self.user_name_input_area = Entry(self.assign_panel_window, width=30)
        # self.user_name_input_area.place(x=110, y=60)
        #
        # self.user_password_entry_area = Entry(self.assign_panel_window, width=30)
        # self.user_password_entry_area.place(x=110, y=100)
        #
        # self.submit_button = Button(self.assign_panel_window, text="Submit", command=self.submit_assign)
        # self.submit_button.place(x=40, y=130)

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

        #self.assign_panel_window.destroy()
        #self.panel_window = None


    def submit_assign(self):

        # hasattr is a python function that checks if a value exists

        # if hasattr(self, 'try_again_label'):
        #    self.try_again_label.destroy()

        # if hasattr(self, 'try_again_label1'):
        #    self.try_again_label.destroy()

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
                self.send_cmd(cmd.encode(), params)


                # get response from server
                res_response, msg_response = Pro.get_msg(self.socket_to_server)
                # if str- dont need to decode
                if isinstance(msg_response, bytes):
                    # retruns True if its in byter
                    msg_response = msg_response.decode()
                if res_response:
                    assign_response = self.handle_assign_response(msg_response)
                    if assign_response: #ASSIGN_ACK
                        print("this is the response!!", msg_response)
                        # only if register Ack- user is assigned!!
                        #moving into Logged In panel
                        self.complete_func() #AssignComplete function in Cli class
                        #self.log_in_panel.init_panel_create()
                    else:
                        if msg_response == "ASSIGN_NACK":
                            print("password is incorrect???")
                        # else- another error


        else:
            self.try_again_label = Label(self.assign_panel_window, text="Username or password are empty! Try again.")
            self.try_again_label.pack()

    def Assign_not_succeeded(self):
        # כנראה לא משתמשת בפונקציה!!
        # Destroy the widgets in the log in window
        self.user_name.destroy()
        self.user_password.destroy()
        self.submit_button.destroy()
        self.user_name_input_area.destroy()
        self.user_password_entry_area.destroy()

        # Create a label indicating successful registration
        Label(self.assign_panel_window, text="Couldn't Log In, Try Again!").pack()

        # Create a button to close the window
        Button(self.assign_panel_window, text="Close", command=self.assign_panel_window.destroy).pack()
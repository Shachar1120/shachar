import threading
from tkinter import *
import tkinter.ttk as ttk

import socket
import pickle
from new_protocol import Pro
from Cli_manger import Cli
import select
from time import time
from pathlib import Path
import pyaudio

class CallStates:
    INIT = 0
    RINGING = 1
    IN_CALL = 2


class RegisterPanel:
    def __init__(self, root, socket_to_server, complete_func, my_port):
        self.root = root
        self.panel_window = None
        self.socket_to_server = socket_to_server
        self.complete_func = complete_func
        self.my_port = my_port

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

    def send_cmd(self, cmd: bytes, params):
        msg_to_send = Pro.create_msg(cmd, params)
        self.socket_to_server.send(msg_to_send)

    def check_if_pickle(self, msg):
        try:
            # Try to unpickle the message
            pickle.loads(msg)
            # If successful, the message is in pickle format
            return True
        except pickle.UnpicklingError:
            # If unsuccessful, the message is not in pickle format
            return False

    def split_message(self, message):
        message_parts = message.split(Pro.PARAMETERS_DELIMITER.encode())  # message: cmd + len(params) + params
        opcode = message_parts[0].decode()
        nof_params = int(message_parts[1].decode())
        params = message_parts[2:]
        return opcode, nof_params, params

    def handle_response_call_target(self, response):
        if response == "TARGET_NACK":
            # they need to call another client
            print("the person you wanted to call to isn't assigned yet")
            print("call another person(from contacts)")
            return False
        elif response == "TARGET_ACK":
            return True

    def handle_cmd(self, cmd):
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
    def get_response(self):
        res, message = Pro.get_msg(self.socket_to_server)
        if not res:
            return False, message
        return True, message
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
        password = self.user_password_entry_area.get()
        my_port = str(self.my_port)


        # Check if username and password are not empty
        if username.strip() and password.strip():
            print("the params:", username, password)

            params = [username.encode(), password.encode(), my_port.encode()]
            if not Pro.check_cmd_and_params(cmd, params):
                # Register_not_succeeded!!
                self.try_again_label1 = Label(self.register_panel_window, text="Couldn't Register! Try Again.")
                self.try_again_label1.pack()

                # self.Register_not_succeeded(newWindow)

            else:
                # send cmd and params(username, password) to server
                self.send_cmd(cmd.encode(), params)
                # get response from server
                res_response, msg_response = self.get_response()
                if res_response:
                    opcode, nof_params, params = self.split_message(msg_response)
                    #res_split_msg, cmd_response, params_response = self.split_message(msg_response)

                    # res_response = False: only got cmd (like in REGISTER N/ACK, ASSIGN N/ACK)
                    if (opcode == "REGISTER_NACK") or (opcode == "REGISTER_ACK"):
                        print("cmd is register")
                        response = self.handle_response_Register(opcode)

                        if not response:  # if false = REGISTER_NACK
                            # checking if the lable already exists
                            if not hasattr(self, 'already_registered_try_again'):
                                self.already_registered_try_again = Label(self.register_panel_window,
                                                                          text="User Already Registered! Try To Log Inq Use Differente Username")
                                self.already_registered_try_again.pack()

                            print(
                                "couldn't register (client already registered)")  # couldn't register/ client exists
                            print("continue to assign")
                            # client already exists! we need to continue to assign too
                            pass
                        else:
                            self.complete_func() #RegisterComplete function in Cli class
                            #self.move_to_home_screen()
                            print("you registered successfully")


                            pass

        else:
            self.try_again_label = Label(self.register_panel_window, text="Username or password are empty! Try again.")
            self.try_again_label.pack()

    def move_to_home_screen(self):
        self.init_panel_destroy()
        #self.home_screen_obj = self.init_panel_create()
        #self.home_screen_obj.init_panel_create()



    def init_panel_create(self):
        # before class it was Register_window function!!!
        # Toplevel object which will
        # be treated as a new window
        self.register_panel_window = self.root

        # sets the title of the
        # Toplevel widget
        self.register_panel_window.title("Register")




        # the label for user_name
        self.user_name = Label(self.register_panel_window, text="Username")
        self.user_name.place(x=40, y=60)

        # the label for user_password
        self.user_password = Label(self.register_panel_window, text="Password")
        self.user_password.place(x=40, y=100)

        self.user_name_input_area = Entry(self.register_panel_window, width=30)
        self.user_name_input_area.place(x=110, y=60)

        self.user_password_entry_area = Entry(self.register_panel_window, width=30)
        self.user_password_entry_area.place(x=110, y=100)

        self.submit_button = Button(self.register_panel_window, text="Submit", command=self.submit_register)
        self.submit_button.place(x=40, y=130)




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
        #self.register_panel_window.destroy()
        #self.register_panel_window = None


    def Register_not_succeeded(self):
        # Destroy the widgets in the registration window
        self.user_name.destroy()
        self.user_password.destroy()
        self.submit_button.destroy()
        self.user_name_input_area.destroy()
        self.user_password_entry_area.destroy()

        # Create a label indicating successful registration
        Label(self.register_panel_window, text="Couldn't register, Try Again!").pack()

        # Create a button to close the window
        Button(self.register_panel_window, text="Close", command=self.register_panel_window.destroy).pack()


class AssignPanel:
    def __init__(self, root, socket_to_server, complete_func):

        self.root = root
        self.panel_window = None
        self.socket_to_server = socket_to_server
        self.complete_func = complete_func
        self.assign_response = None

    def handle_response_assign(self, response):
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
        try:
            # Try to unpickle the message
            pickle.loads(msg)
            # If successful, the message is in pickle format
            return True
        except pickle.UnpicklingError:
            # If unsuccessful, the message is not in pickle format
            return False

    def split_message(self, message):
        message_parts = message.split(Pro.PARAMETERS_DELIMITER.encode())  # message: cmd + len(params) + params
        opcode = message_parts[0].decode()
        nof_params = int(message_parts[1].decode())
        params = message_parts[2:]
        return opcode, nof_params, params

    def handle_response_call_target(self, response):
        if response == "TARGET_NACK":
            # they need to call another client
            print("the person you wanted to call to isn't assigned yet")
            print("call another person(from contacts)")
            return False
        elif response == "TARGET_ACK":
            return True

    def handle_cmd(self, cmd):
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
    def get_response(self):
        res, message = Pro.get_msg(self.socket_to_server)
        if not res:
            return False, message
        return True, message

    def handle_assign_response(self, msg):
        msg = msg.decode()
        msg_parts = msg.split(" ")
        print(msg_parts[0], "," , msg_parts[1])
        if msg_parts[0] == "ASSIGN_ACK":
            return True
        else:
            return False


    def init_panel_create(self):
        # before class it was Assign_Window function!!!
        # Toplevel object which will
        # be treated as a new window

        self.assign_panel_window = self.root
        # sets the title of the
        self.assign_panel_window.title("Log In")

        # sets the geometry of toplevel
        self.assign_panel_window.geometry("600x400")

        # the label for user_name
        self.user_name = Label(self.assign_panel_window, text="Username")
        self.user_name.place(x=40, y=60)

        # the label for user_password
        self.user_password = Label(self.assign_panel_window, text="Password")
        self.user_password.place(x=40, y=100)

        self.user_name_input_area = Entry(self.assign_panel_window, width=30)
        self.user_name_input_area.place(x=110, y=60)

        self.user_password_entry_area = Entry(self.assign_panel_window, width=30)
        self.user_password_entry_area.place(x=110, y=100)

        self.submit_button = Button(self.assign_panel_window, text="Submit", command=self.submit_assign)
        self.submit_button.place(x=40, y=130)

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
                res_response, msg_response = self.get_response()
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

class ButtonItem:
    def __init__(self, item, call_func, dict):
        self.item = item
        self.call_handling = None
        self.dict = dict
        self.call_func = call_func

    def item_clicked(self):
        print(f"Clicked item: {self.item}")
        clicked_item = {self.item}
        self.call_func(self.item, self.dict) # call func is make call (of ContactsPanel class)



class ContactsPanel:
    INIT = 0
    RINGING = 1
    IN_CALL = 2


    def __init__(self, root, socket_to_server, complete_func, move_to_ringing, move_to_call_receiving, profile, call_initiate_socket):
        self.profile = profile
        self.root = root
        self.panel_window = None
        self.socket_to_server = socket_to_server
        self.complete_func = complete_func
        self.item = None
        self.button_objs = []
        self.button_widgets = []
        self.assigned_clients_dict = None
        self.item_list = None
        self.move_to_ringing = move_to_ringing
        self.move_to_call_receiving = move_to_call_receiving
        self.state = CallStates.INIT
        self.transition = False

        self.call_initiate_socket = call_initiate_socket


    def get_response(self):
        res, message = Pro.get_msg(self.socket_to_server)
        if not res:
            return False, message
        return True, message

    def split_message(self, message):

        message_parts = message.split(Pro.PARAMETERS_DELIMITER.encode())  # message: cmd + len(params) + params
        opcode = message_parts[0].decode()
        nof_params = int(message_parts[1].decode())
        params = message_parts[2:]
        return opcode, nof_params, params

    def send_cmd(self, cmd: bytes, params):
        msg_to_send = Pro.create_msg(cmd, params)
        self.socket_to_server.send(msg_to_send)

    def check_if_pickle(self, msg):
        try:
            # Try to unpickle the message
            pickle.loads(msg)
            # If successful, the message is in pickle format
            return True
        except pickle.UnpicklingError:
            # If unsuccessful, the message is not in pickle format
            return False

    def send_cmd_to_other_client(self, cmd: bytes, params):
        msg_to_send = Pro.create_msg(cmd, params)
        self.call_initiate_socket.send(msg_to_send)

    def handle_response_call_target(self, response):
        if response == "TARGET_NACK":
            # they need to call another client
            print("the person you wanted to call to isn't assigned yet")
            print("call another person(from contacts)")
            return False
        elif response == "TARGET_ACK":
            return True


    def init_panel_create(self):

        self.init_network()
        # יצירת תהליך חדש שמחכה לפתיחת שיחה
        thread = threading.Thread(target=self.wait_for_network)

        # הפעלת התהליך
        thread.start()

        self.Logged_In_window = self.root
        self.Logged_In_window.title("Your Contacts:")

        cmd = "CONTACTS"
        params = []
        # send cmd and params(username, password) to server
        self.send_cmd(cmd.encode(), params)

        # get response from server
        # מקבל את הרשימת לקוחות הרשומים כדי להציג ללקוח
        # צריכה למחוק את הלקוח שאני מהרשימת אנשי קשר
        res_response, msg_response = self.get_response()
        if res_response:
            opcode, nof_params, params = self.split_message(msg_response)

            #res_split_msg, cmd_response, params_response = self.split_message(msg_response)
            #print("dict??", params_response)

            # opcode = False: only got cmd (like in REGISTER N/ACK, ASSIGN N/ACK)
            if (opcode == "ASSIGNED_CLIENTS"):
                print("got the dict!!!", params[0])
                self.assigned_clients_dict = pickle.loads(params[0])
                self.item_list = list(self.assigned_clients_dict.keys())



                # רשימת הפריטים
                items = self.item_list
                # יצירת כפתורים לכל פריט ברשימה
                cget_bg = self.root.cget("bg")
                print(f"lets see: {cget_bg}")
                for item in items:
                    obj = ButtonItem(item, self.make_ring, self.assigned_clients_dict)
                    button = ttk.Button(self.root, text=item, command=obj.item_clicked)
                    button.pack(pady=5, padx=10, fill="x")
                    self.button_objs.append(obj)
                    self.button_widgets.append(button)


    def init_panel_destroy(self):
        for button in self.button_widgets:
            print(f"type of button {type(button)}")
            button.destroy()
        self.button_objs = []
        self.button_widgets = []
            #self.button_objs = []
        #self.Logged_In_window.destroy()



    ###################################
    # network handling part:
    ###################################

    def init_network(self):
        # open socket with the server
        self.call_initiate_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.call_accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.call_accept_socket.bind(("0.0.0.0", self.profile.call_accept_port))
        self.call_accept_socket.listen()

        # self.call_obj = None
        self.loggedIn_obj = None


    ################################
    # network ==> responder ... secondary thread
    ################################
    def wait_for_network(self):

        while True:
            rlist, _, _ = select.select([self.socket_to_server, self.call_initiate_socket, self.call_accept_socket], [], [])

            for s in rlist:
                if s == self.socket_to_server: #connect with server
                    pass
                elif s == self.call_accept_socket: #for call establishment
                    self.call_initiate_socket, _ = self.call_accept_socket.accept()
                    print("Client connected")

                elif self.call_initiate_socket: # for call handling

                    res, message = Pro.get_msg(self.call_initiate_socket)
                    print(f"wait_for_network: {message}")
                    if res:
                        print("the message is:", message)
                        opcode, nof_params, params = self.split_message(message)
                        #res_split_msg, cmd_response, params_response = self.split_message(message)

                        if opcode == "RING":
                            print("received call")
                            #tkinter after
                            #move_to_call_receiving
                            self.state = CallStates.RINGING
                            self.transition = True
                        elif opcode == "IN_CALL":
                            print("got in call!!")
                            self.state = CallStates.IN_CALL
                            self.transition = True
                            CHUNK = 4096
                            FORMAT = pyaudio.paInt16
                            CHANNELS = 1
                            RATE = 44100
                            RECORD_SECONDS = 10
                            self.p = pyaudio.PyAudio()
                            self.stream_input = self.p.open(format=FORMAT,
                                                        channels=CHANNELS,
                                                        rate=RATE,
                                                        input=True,
                                                        input_device_index=self.profile.my_mic,
                                                        frames_per_buffer=CHUNK)
                            self.stream_output = self.p.open(format=FORMAT,
                                                        channels=CHANNELS,
                                                        rate=RATE,
                                                        output=True,  # for speaker
                                                        input_device_index=self.profile.my_speaker,
                                                        frames_per_buffer=CHUNK)



                        elif opcode == "FRAME":
                            #accept frame and play
                            data = Pro.PARAMETERS_DELIMITER.encode().join(params) # split msg broke the pickle data by PARAMETERS_DELIMITER, so we combined it bak
                            #data = pickle.loads(data)
                            print(f"got frame: {data}")
                            self.stream_output.write(data)
                            pass

                        else:
                            pass

                    else:
                        print("didnt get the message")


    def handle_connection_failed(self):
        pass



    ################################
    # network ==> caller ... main thread
    ################################

    def make_ring(self, item, dict):

        #need to get client details dictionary
        # item is username of wanted client
        # need to get detailes of that client from dict
        self.assigned_clients_dict = dict
        print("got the dict!!", self.assigned_clients_dict)

        if item in self.assigned_clients_dict:
            print(f"item exists in dict: '{item}' is: {self.assigned_clients_dict[item]}")
            try:
                # make the connection
                # point to point
                self.other_client_port = self.assigned_clients_dict[item][1]
                self.call_initiate_socket.connect(("127.0.0.1", self.other_client_port)) # self.call_initiate_port
                print("client connected")
            except Exception as ex:
                print("client couldnt connect")
                self.handle_connection_failed()  # missing exception handling
                return
            try:
                # start ringing!!!!

                cmd = "RING"
                self.port_num_str = str(self.other_client_port)
                params = [item.encode(), self.port_num_str.encode()] # sends username, port



                #send it to the other client!!! not to server
                #because the socket is between the 2 clients now
                self.send_cmd_to_other_client(cmd.encode(), params)

                # move to new panel
                # sending root for socket_to_server and root
                self.move_to_ringing()
            except Exception as ex:
                print(ex)
        else:
            print(f"cant call '{item}' , he doesnot exist in the dictionary.")


class CallConnectHandling:
    def __init__(self, root, socket_to_server, complete_func, move_to_call_receiving, profile, call_initiate_socket):
        self.profile = profile
        self.root = root
        self.panel_window = None
        self.socket_to_server = socket_to_server
        self.complete_func = complete_func
        self.item = None
        self.button_objs = []
        self.button_widgets = []
        self.assigned_clients_dict = None
        self.item_list = None
        self.move_to_call_receiving = move_to_call_receiving
        self.state = CallStates.INIT
        self.transition = False

        self.call_initiate_socket = call_initiate_socket


    def init_panel_destroy(self):
        self.call_who.destroy()
        self.enter_username.destroy()
        self.username_input_area.destroy()
        self.btn_contact.destroy()
        self.call_window.destroy()




    def wait_for_ring(self):
        pass

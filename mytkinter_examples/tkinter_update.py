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



class RegisterPanel:
    def __init__(self, root, my_socket, complete_func, my_port):
        self.root = root
        self.panel_window = None
        self.my_socket = my_socket
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
        self.my_socket.send(msg_to_send)

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
        if self.check_if_pickle(message):
            # עובד רק נכון לכרגע, אני מניחה כרגע שהדבר היחיד שאני מקבלת בפיקל הוא המילון, אני לא שולחת את הפקודה אלא יוצרת אותה
            # אם בעתיד אשלח עוד דברים בפיקל אצטרך להבדיל ביניהם!!!
            print("got the dict!!!!")
            cmd = "ASSIGNED_CLIENTS"
            # load pickle and not decode to get msg!!
            received_dict = pickle.loads(message)
            return True, cmd, received_dict
            # msg = received_dict
        else:
            msg = message.decode()
        message_parts = msg.split(Pro.PARAMETERS_DELIMITER)  # message: cmd + len(params) + params
        print("0:" + message_parts[0] + "1:" + message_parts[1])
        if message_parts[1] == '0':
            print("False!! no params, only cmd")
            return False, message_parts[0], None  # return only cmd
        else:
            return True, message_parts[0], message_parts[2:]  # return cmd, params

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
            self.my_socket.send(sending_cmd)

            # receiving from server
            # self.handle_server_response(cmd, None)
            # if cmd == 'EXIT':
            #    return False
        # else:
        # print("Not a valid command, or missing parameters\n")

        return True
    def get_response(self):
        res, message = Pro.get_msg(self.my_socket)
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
                    res_split_msg, cmd_response, params_response = self.split_message(msg_response)
                    if not res_split_msg:
                        # res_response = False: only got cmd (like in REGISTER N/ACK, ASSIGN N/ACK)
                        if (cmd_response == "REGISTER_NACK") or (cmd_response == "REGISTER_ACK"):
                            print("cmd is register")
                            response = self.handle_response_Register(cmd_response)

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
    def __init__(self, root, my_socket, complete_func):

        self.root = root
        self.panel_window = None
        self.my_socket = my_socket
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
        self.my_socket.send(msg_to_send)

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
        if self.check_if_pickle(message):
            # עובד רק נכון לכרגע, אני מניחה כרגע שהדבר היחיד שאני מקבלת בפיקל הוא המילון, אני לא שולחת את הפקודה אלא יוצרת אותה
            # אם בעתיד אשלח עוד דברים בפיקל אצטרך להבדיל ביניהם!!!
            print("got the dict!!!!")
            cmd = "ASSIGNED_CLIENTS"
            # load pickle and not decode to get msg!!
            received_dict = pickle.loads(message)
            return True, cmd, received_dict
            # msg = received_dict
        else:
            msg = message.decode()
        message_parts = msg.split(Pro.PARAMETERS_DELIMITER)  # message: cmd + len(params) + params
        print("0:" + message_parts[0] + "1:" + message_parts[1])
        if message_parts[1] == '0':
            print("False!! no params, only cmd")
            return False, message_parts[0], None  # return only cmd
        else:
            return True, message_parts[0], message_parts[2:]  # return cmd, params

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
            self.my_socket.send(sending_cmd)

            # receiving from server
            # self.handle_server_response(cmd, None)
            # if cmd == 'EXIT':
            #    return False
        # else:
        # print("Not a valid command, or missing parameters\n")

        return True
    def get_response(self):
        res, message = Pro.get_msg(self.my_socket)
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


    def __init__(self, root, s_to_server, complete_func, move_to_calling, move_to_call_receiving, server_port, connect_port):
        self.server_port = server_port
        self.root = root
        self.panel_window = None
        self.s_to_server = s_to_server
        self.connect_port = connect_port
        self.complete_func = complete_func
        self.item = None
        self.button_objs = []
        self.button_widgets = []
        self.assigned_clients_dict = None
        self.item_list = None
        self.move_to_calling = move_to_calling
        self.move_to_call_receiving = move_to_call_receiving
        self.state = ContactsPanel.INIT
        self.transition = False


    def get_response(self):
        res, message = Pro.get_msg(self.s_to_server)
        if not res:
            return False, message
        return True, message

    def split_message(self, message):
        if self.check_if_pickle(message):
            # עובד רק נכון לכרגע, אני מניחה כרגע שהדבר היחיד שאני מקבלת בפיקל הוא המילון, אני לא שולחת את הפקודה אלא יוצרת אותה
            # אם בעתיד אשלח עוד דברים בפיקל אצטרך להבדיל ביניהם!!!
            print("got the dict!!!!")
            cmd = "ASSIGNED_CLIENTS"
            # load pickle and not decode to get msg!!
            received_dict = pickle.loads(message)
            return True, cmd, received_dict
            # msg = received_dict
        else:
            msg = message.decode()
        message_parts = msg.split(Pro.PARAMETERS_DELIMITER)  # message: cmd + len(params) + params
        print("0:" + message_parts[0] + "1:" + message_parts[1])
        if message_parts[1] == '0':
            print("False!! no params, only cmd")
            return False, message_parts[0], None  # return only cmd
        else:
            return True, message_parts[0], message_parts[2:]  # return cmd, params

    def send_cmd(self, cmd: bytes, params):
        msg_to_send = Pro.create_msg(cmd, params)
        self.s_to_server.send(msg_to_send)

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
        self.sock_initiate_call.send(msg_to_send)

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
            res_split_msg, cmd_response, params_response = self.split_message(msg_response)
            print("dict??", params_response)
            if res_split_msg:
                # res_response = False: only got cmd (like in REGISTER N/ACK, ASSIGN N/ACK)
                if (cmd_response == "ASSIGNED_CLIENTS"):
                    print("got the dict!!!", params_response)
                    self.assigned_clients_dict = params_response
                    self.item_list = list(params_response.keys())
        if not res_response:
            print("didnt get message!!!")

        # רשימת הפריטים
        items = self.item_list
        # יצירת כפתורים לכל פריט ברשימה
        cget_bg = self.root.cget("bg")
        print(f"lets see: {cget_bg}")
        for item in items:
            obj = ButtonItem(item, self.make_call, self.assigned_clients_dict)
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



    def call_button(self):
        call_window = self.root
        # sets the title of the
        # Toplevel widget
        call_window.title("Call")


        self.call_who = Label(call_window, text="Who Do You Want To Call To?")
        self.call_who.place(x=180, y=60)

        self.enter_username = Label(call_window, text="Enter Username:")
        self.enter_username.place(x=40, y=100)

        self.username_input_area = Entry(call_window, width=30)
        self.username_input_area.place(x=130, y=100)

        # Create a Button
        self.btn_contact = Button(call_window, text='submit', command=self.submit_call)
        self.btn_contact.place(x=150, y=150)


    def submit_call(self):
        cmd = "CALL"
        username = self.username_input_area.get()
        # Check if username is not empty
        if username.strip():
            print("he wants to call:", username)
            target_username = self.username_input_area.get()

            params = [target_username.encode()]
            if not Pro.check_cmd_and_params(cmd, params):
                # in this phase only REGISTER or ASSIGN is required with [username, password] as params
                print("Invalid command! Try again!")

                # user isnt registered!!!
                self.try_again_label1 = Label(self.root, text="Invalid command! Try again!")
                self.try_again_label1.pack()

            self.send_cmd(cmd.encode(), params)

            res_response, msg_response = self.get_response()
            if res_response:
                res_split_msg, cmd_response, params_response = self.split_message(msg_response)
                if res_split_msg:
                    # res_response = True: got cmd and params (meaning cmd = ASSIGNED_CLIENTS)
                    if (cmd_response == "TARGET_NACK") or (cmd_response == "TARGET_ACK"):
                        print("cmd is call(call target client)")
                        client_username = params_response[0]
                        response = self.handle_response_call_target(cmd_response)
                        if response:  # if true = ASSIGN_ACK
                            print("we can call target! he is assigned")

                            # get target details
                            # getting target details from server dict client_sockets_details
                            # getting ip and port according to username

                            cmd = "ASK_TARGET_DETAILS"
                            tof = Pro.check_cmd(cmd)
                            if tof:
                                # sending to server
                                cmd_send = Pro.create_msg(cmd.encode(), [client_username.encode()])
                                self.s_to_server.send(cmd_send)

                            # get response from server
                            # should i wait for response from server??? not assume i get it
                            res_response, msg_response = self.get_response()
                            if res_response:
                                res_split_msg1, cmd_response1, params_response1 = self.split_message(msg_response)
                                if res_split_msg1:
                                    # res_response = True: got cmd and params
                                    if (cmd_response1 == "SEND_TARGET_DETAILS"):
                                        print("cmd is SEND_TARGET_DETAILS")
                                        client_socket_details = params_response1
                                        print("got the client details params!!!:", client_socket_details)
                            pass

                        else:  # REGISTER_NACK- Maybe user already exist!!! try different username
                            print("couldn't call target!")
                            print("call another person: (from contacts)")


        else:
            self.try_again_label2 = Label(self.root, text="It's Empty! Write again")
            self.try_again_label2.pack()


    ###################################
    # network handling part:
    ###################################

    def init_network(self):
        # open socket with the server
        self.sock_initiate_call = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_accept_call = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_accept_call.bind(("0.0.0.0", self.server_port))
        self.sock_accept_call.listen()

        # self.call_obj = None
        self.loggedIn_obj = None


    ################################
    # network ==> responder ... secondary thread
    ################################
    def wait_for_network(self):

        while True:
            rlist, _, _ = select.select([self.s_to_server, self.sock_initiate_call, self.sock_accept_call], [], [])

            for s in rlist:
                if s == self.s_to_server: #connect with server
                    pass
                elif s == self.sock_accept_call: #for call establishment
                    self.sock_initiate_call, _ = self.sock_accept_call.accept()
                    print("Client connected")

                elif self.sock_initiate_call: # for call handling

                    res, message = Pro.get_msg(self.sock_initiate_call)
                    if res:
                        print("the message is:", message)
                        res_split_msg, cmd_response, params_response = self.split_message(message)
                        if res_split_msg:
                            if cmd_response == "RING":
                                #tkinter after
                                #move_to_call_receiving
                                self.state = ContactsPanel.RINGING
                                self.transition = True

                    else:
                        print("didnt get the message")


    def handle_connection_failed(self):
        pass

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
        if self.check_if_pickle(message):
            # עובד רק נכון לכרגע, אני מניחה כרגע שהדבר היחיד שאני מקבלת בפיקל הוא המילון, אני לא שולחת את הפקודה אלא יוצרת אותה
            # אם בעתיד אשלח עוד דברים בפיקל אצטרך להבדיל ביניהם!!!
            print("got the dict!!!!")
            cmd = "ASSIGNED_CLIENTS"
            # load pickle and not decode to get msg!!
            received_dict = pickle.loads(message)
            return True, cmd, received_dict
            # msg = received_dict
        else:
            msg = message.decode()
        message_parts = msg.split(Pro.PARAMETERS_DELIMITER)  # message: cmd + len(params) + params
        print("0:" + message_parts[0] + "1:" + message_parts[1])
        if message_parts[1] == '0':
            print("False!! no params, only cmd")
            return False, message_parts[0], None  # return only cmd
        else:
            return True, message_parts[0], message_parts[2:]  # return cmd, params

    ################################
    # network ==> caller ... main thread
    ################################

    def make_call(self, item, dict):

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
                self.sock_initiate_call.connect(("127.0.0.1", self.other_client_port)) # self.connect_port
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

                #move to new panel
                # sending root for my_socket and root
                self.move_to_calling()

                #send it to the other client!!! not to server
                #because the socket is between the 2 clients now
                self.send_cmd_to_other_client(cmd.encode(), params)
            except Exception as ex:
                print(ex)



        else:
            print(f"cant call '{item}' , he doesnot exist in the dictionary.")



class CallConnectHandling:
    def __init__(self, root, my_socket, complete_func):

        self.root = root
        self.panel_window = None
        self.my_socket = my_socket
        self.ringing_window = None


    def init_panel_destroy(self):
        self.call_who.destroy()
        self.enter_username.destroy()
        self.username_input_area.destroy()
        self.btn_contact.destroy()
        self.call_window.destroy()




    def wait_for_ring(self):
        pass



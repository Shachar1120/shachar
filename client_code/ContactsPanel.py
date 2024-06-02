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

class CallStates:
    INIT = 0
    RINGING = 1
    IN_CALL = 2

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


    def __init__(self, root, socket_to_server, complete_func, move_to_ringing, move_to_call_receiving, profile, call_initiate_socket, init_answer_and_hangup_buttons):
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
        self.init_answer_and_hangup_buttons = init_answer_and_hangup_buttons


    def split_message2(self, message):

        message_parts = message.split(Pro.PARAMETERS_DELIMITER)  # message: cmd + len(params) + params
        opcode = message_parts[0]
        nof_params = int(message_parts[1])
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

    def split_assigned_clients_msg(self, message):
        message_parts = message.split(Pro.PARAMETERS_DELIMITER.encode())  # .encode() # message: cmd + len(params) + params
        opcode = message_parts[0].decode
        nof_params = int(message_parts[1].decode())
        params = message_parts[2:][0]
        # params in this case is the pickle dict!!!
        print("split_assigned_clients_msg:", params)
        return opcode, nof_params, params
    def split_message3(self, message):
        message_parts = message.split(Pro.PARAMETERS_DELIMITER.encode())  # .encode() # message: cmd + len(params) + params
        opcode = message_parts[0]
        nof_params = int(message_parts[1])
        params = message_parts[2:]
        # params in this case is the pickle dict!!!
        print("split_message3:", opcode, nof_params, params)
        return opcode, nof_params, params

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
        res_response, msg_response = Pro.get_msg(self.socket_to_server) # getting msg: b"ASSIGNED_CLIENTS ! /x80...(dict in pickle)"
        if res_response:
            #opcode is ASSIGNED_CLIENTS
            opcode, nof_params, params = self.split_assigned_clients_msg(msg_response)
            self.assigned_clients_dict = pickle.loads(params)
            print("got the dict!!!", self.assigned_clients_dict)
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
                    opcode, nof_params, params = self.split_message3(message)
                    opcode = opcode.decode()
                    print(f"wait_for_network: {message}")
                    if res:
                        print("the message is:", opcode, nof_params, params)

                        if opcode == "RING":
                            params = params[0].decode()
                            print("received call")
                            #tkinter after
                            #move_to_call_receiving
                            self.state = CallStates.RINGING
                            self.transition = True
                            self.init_answer_and_hangup_buttons()
                        elif opcode == "IN_CALL":
                            #params = params[0].decode()
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
                            data = params[0]
                            print("FRAME params!!! (data)", params)
                            #accept frame and play
                            #data = Pro.PARAMETERS_DELIMITER.encode().join(params) # split msg broke the pickle data by PARAMETERS_DELIMITER, so we combined it bak
                            data = pickle.loads(data)
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
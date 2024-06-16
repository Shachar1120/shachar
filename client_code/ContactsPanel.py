import threading
from multiprocessing import Process
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
from call_utilities import *
from DataBase import DataBase

class ButtonItem:
    def __init__(self, item, call_func, dict):
        self.item = item
        self.call_handling = None
        self.dict = dict
        self.call_func = call_func

    def item_clicked(self):
        print(f"Clicked item: {self.item}")
        clicked_item = {self.item}
        self.call_func(self.item, self.dict) # call func is make ring (of ContactsPanel class)

class ContactsPanel:
    INIT = 0
    RINGING = 1
    IN_CALL = 2


    def __init__(self, root, socket_to_server, complete_func, move_to_ringing_initiator, profile, networking_obj):
        self.profile = profile
        self.root = root
        self.panel_window = None
        self.socket_to_server = socket_to_server
        self.complete_func = complete_func #)לא רלוונטית יותר??)
        self.item = None
        self.button_objs = []
        self.button_widgets = []
        self.assigned_clients_dict = None
        self.item_list = None
        self.move_to_ringing_initiator = move_to_ringing_initiator
        self.state = CallStates.INIT
        self.transition = False
        self.vow1 = None
        self.vow2 = None

        self.username = None
        self.database_obj = DataBase("mydatabase")


        self.networking_obj = networking_obj


    # def split_message2(self, message):
    #
    #     message_parts = message.split(Pro.PARAMETERS_DELIMITER)  # message: cmd + len(params) + params
    #     opcode = message_parts[0]
    #     nof_params = int(message_parts[1])
    #     params = message_parts[2:]
    #     return opcode, nof_params, params

    def send_cmd(self, cmd: bytes, params):
        msg_to_send = Pro.create_msg(cmd, params)
        self.socket_to_server.send(msg_to_send)



    def send_cmd_to_other_client(self, cmd: bytes, params):
        msg_to_send = Pro.create_msg(cmd, params)
        self.networking_obj.call_initiate_socket.send(msg_to_send)



    def split_assigned_clients_msg(self, message):
        #message_parts = message.split(Pro.PARAMETERS_DELIMITER.encode())  # .encode() # message: cmd + len(params) + params
        #opcode = message_parts[0].decode
        #nof_params = int(message_parts[1].decode())
        #params = message_parts[2:]
        # params in this case is the pickle dict!!!
        #print("split_assigned_clients_msg:", params)
        opcode, nof_params, params = Pro.split_message(message)
        return opcode, nof_params, params[0]
    def split_message3(self, message):
        # כנראה שלא רלוונטית
        message_parts = message.split(Pro.PARAMETERS_DELIMITER.encode())  # .encode() # message: cmd + len(params) + params
        opcode = message_parts[0].decode()
        nof_params = int(message_parts[1].decode())
        params = message_parts[2:]
        # params in this case is the pickle dict!!!
        print("split_message3:", opcode, nof_params, params)
        return opcode, nof_params, params

    def init_panel_create(self):

        # self.init_network()
        # # יצירת תהליך חדש שמחכה לפתיחת שיחה
        # thread = threading.Thread(target=self.wait_for_network)
        #
        # # הפעלת התהליך
        # thread.start()


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
            opcode, nof_params, params = Pro.split_message(msg_response)
            params = params[0]
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

        #for synchronizing the contacts
            #self.vow1 = Process(target=self.vow1, args=(self.assigned_clients_dict,))
            #self.vow2 = Process(target=self.vow2, args=(self.assigned_clients_dict,))




    def init_panel_destroy(self):
        for button in self.button_widgets:
            print(f"type of button {type(button)}")
            button.destroy()
        self.button_objs = []
        self.button_widgets = []
            #self.button_objs = []
        #self.Logged_In_window.destroy()





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
            self.username = item
            try:
                # make the connection
                # point to point
                self.other_client_port = int(self.assigned_clients_dict[item][1])
                self.networking_obj.call_initiate_socket.connect(("127.0.0.1", self.other_client_port)) # self.call_initiate_port
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
                self.move_to_ringing_initiator()
            except Exception as ex:
                print(ex)
        else:
            print(f"cant call '{item}' , he doesnot exist in the dictionary.")
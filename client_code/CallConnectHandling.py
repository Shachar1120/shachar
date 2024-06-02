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
from call_utilities import *

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
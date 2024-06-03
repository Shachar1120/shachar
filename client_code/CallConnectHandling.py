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
    def __init__(self, root, socket_to_server, complete_func, profile, call_initiate_socket, call_transmit, move_to_call_receiving):
        self.profile = profile
        self.root = root
        self.call_who = None
        self.calling_image = None

        self.panel_window = None
        self.socket_to_server = socket_to_server
        self.complete_func = complete_func
        self.item = None
        self.button_objs = []
        self.button_widgets = []
        self.assigned_clients_dict = None
        self.item_list = None
        self.state = CallStates.INIT
        self.transition = False
        self.images = {}
        self.call_transmit = call_transmit
        self.move_to_call_receiving = move_to_call_receiving

        self.call_initiate_socket = call_initiate_socket

        self.transition = False
        self.state = CallStates.INIT

    def load_image(self, path, size=None):
        # פונקציה לטעינת תמונה והמרתה לפורמט Tkinter
        image = Image.open(path)
        if size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def init_panel_initiator_create(self): # for ringing

        self.root.title("Ringing")

        self.root.configure(bg='#2f2f2f')

        # Label for "calling..." text
        self.call_who = Label(self.root, text="calling...", font=("Garet", 24), bg='#2f2f2f', fg='white')
        self.call_who.pack(pady=40)

        # Paths to images
        ring_image_path = r"..\images\ring1.png"

        # Load the submit button image
        self.images['ring_image_path'] = self.load_image(ring_image_path)


        #self.image_label = Label(self.root, image=self.images['ring_image_path'], bg='#2f2f2f')
        #self.image_label.image = self.images['ring_image_path']  # Keep a reference to avoid garbage collection
        #self.image_label.pack(pady=20)

        # Create a Button
        photo = PhotoImage(file=r"..\images\ring1.png")
        photoimage1 = photo.subsample(3, 3)
        photo = PhotoImage(file=r"..\images\ring2.png")
        photoimage2 = photo.subsample(3, 3)
        photo = PhotoImage(file=r"..\images\ringing1.png")
        photoimage3 = photo.subsample(3, 3)


        button_array = [photoimage1, photoimage2, photoimage3]
        self.calling_image = Label(self.root, image=button_array[0])
        self.calling_image.place(x=200, y=100)
        self.calling_image.image = button_array
        self.calling_image.image_id = 0

        self.animate_handle()
        self.state = CallStates.RINGING
        self.transition = True

    def destroy_panel_initiator_create(self):
        self.call_who.destroy()
        self.calling_image.destroy()

    def init_panel_acceptor_create(self):
        print("moved to init_answer_and_hangup_buttons!!!")
        # sets the title of the
        # Toplevel widget

        #self.call_who = Label(self.root, text="Someone is ringing")
        #self.call_who.place(x=180, y=60)
        self.call_who = Label(self.root, text="... is calling")
        self.call_who.place(x=180, y=60)

        self.root.title("Incoming Call")

        self.photo_answer = PhotoImage(file=r"..\images\answer.png").subsample(3, 3)
        self.photo_hang_up = PhotoImage(file=r"..\images\hang_up.png").subsample(3, 3)

        # Create buttons
        self.btn_hang_up = Button(self.root, image=self.photo_hang_up, command=self.hang_up_call,
                                  borderwidth=0)
        self.btn_hang_up.image = self.photo_hang_up  # keep a reference to avoid garbage collection
        self.btn_hang_up.pack(side=LEFT, padx=20, pady=20)

        self.btn_answer = Button(self.root, image=self.photo_answer, command=self.move_to_call_receiving,
                                 borderwidth=0)
        self.btn_answer.image = self.photo_answer  # keep a reference to avoid garbage collection
        self.btn_answer.pack(side=RIGHT, padx=10, pady=20)

        # Create a Button
        photo = PhotoImage(file=r"..\images\ring1.png")
        photoimage1 = photo.subsample(3, 3)
        photo = PhotoImage(file=r"..\images\ring2.png")
        photoimage2 = photo.subsample(3, 3)
        photo = PhotoImage(file=r"..\images\ringing1.png")
        photoimage3 = photo.subsample(3, 3)

        button_array = [photoimage1, photoimage2, photoimage3]
        self.calling_image = Label(self.root, image=button_array[0])
        self.calling_image.place(x=200, y=100)
        self.calling_image.image = button_array
        self.calling_image.image_id = 0
    def destroy_panel_acceptor_create(self):
        self.call_who.destroy()
        self.calling_image.destroy()
        self.btn_hang_up.destroy()
        self.btn_answer.destroy()
    def init_panel_calling(self):
        # sets the title of the
        # Toplevel widget
        self.call_label = Label(self.root, text="In call! as caller")
        self.call_label.place(x=180, y=60)

    def init_panel_call_receiver(self):
        # in call
        self.call_window = self.root
        # sets the title of the
        # Toplevel widget
        self.call_who = Label(self.call_window, text="In call! as call reciever")
        self.call_who.place(x=180, y=60)

        thread = threading.Thread(target=self.call_transmit).start()
    def animate_handle(self):

        self.calling_image.image_id = (self.calling_image.image_id + 1) % 6
        self.calling_image.config(image=self.calling_image.image[self.calling_image.image_id // 3])
    def hang_up_call(self):
        pass
    # def init_panel_destroy(self):
    #     self.call_who.destroy()
    #     self.enter_username.destroy()
    #     self.username_input_area.destroy()
    #     self.btn_contact.destroy()
    #     self.call_window.destroy()




    def wait_for_ring(self):
        pass
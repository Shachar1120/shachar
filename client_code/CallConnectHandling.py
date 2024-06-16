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
from AudioHandling import AudioHandling
from call_utilities import *

class CallConnectHandling:
    INIT = 0
    RINGING = 1
    IN_CALL = 2
    def __init__(self, root, socket_to_server, complete_func, profile, networking_obj, move_to_in_call_acceptor):
        self.profile = profile
        self.root = root
        self.call_who = None
        self.calling_image = None

        self.panel_window = None
        self.socket_to_server = socket_to_server
        self.complete_func = complete_func # לא רלוונטי??
        self.item = None #??
        self.button_objs = []
        self.button_widgets = []
        self.assigned_clients_dict = None
        self.item_list = None
        self.state = CallStates.INIT
        self.transition = False
        self.images = {}
        self.move_to_in_call_acceptor = move_to_in_call_acceptor

        self.networking_obj = networking_obj

        self.transition = False
        self.state = CallStates.INIT

        self.audio_handling = None

        self.networking_obj.register_on_ring(self.on_ring) # for acceptor???
        self.networking_obj.register_in_call(self.in_call)

    def on_ring(self):
        self.transition = True
        self.state = CallStates.RINGING # for acceptor

    def in_call(self):
        self.transition = True
        self.state = CallStates.IN_CALL

    def load_image(self, path, size=None):
        # פונקציה לטעינת תמונה והמרתה לפורמט Tkinter
        image = Image.open(path)
        if size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def init_panel_initiator_create(self): # for ringing

        self.root.title("Ringing")

        #self.root.configure(bg='#2f2f2f')

        # Label for "calling..." text
        self.call_who = Label(self.root, text="calling...", font=("Garet", 24))
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
        self.state = CallStates.RINGING # for initiator
        self.transition = False

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

        self.btn_answer = Button(self.root, image=self.photo_answer, command=self.move_to_in_call_acceptor,
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
    def init_panel_calling(self, username):
        self.root.title("In Call! as caller")

        # Label for "In Call"
        self.call_label = Label(self.root, text="In Call! as caller", font=("Helvetica", 20, "bold"))
        self.call_label.place(relx=0.5, rely=0.3, anchor=CENTER)  # Place label in the center top

        # Label for username
        self.username_label = Label(self.root, text=username, font=("Helvetica", 16))
        self.username_label.place(relx=0.5, rely=0.4, anchor=CENTER)  # Place username label below call label

        self.photo_hang_up = PhotoImage(file=r"..\images\hang_up.png").subsample(3, 3)
        # Hang up button with icon
        self.btn_hang_up = Button(self.root, image=self.photo_hang_up, command=self.hang_up_call, borderwidth=0)
        self.btn_hang_up.image = self.photo_hang_up  # keep a reference to avoid garbage collection
        self.btn_hang_up.place(relx=0.5, rely=0.7, anchor=CENTER)  # Place button at the center bottom
        # self.root.title("In Call! as caller")
        #
        # #self.root.configure(bg='#2f2f2f')
        #
        # # Label for "calling..." text
        # #self.call_who = Label(self.root, text="Called...", font=("Garet", 24), bg='#2f2f2f', fg='white')
        # #self.call_who.pack(pady=40)
        #
        #
        # self.label_username = username
        #
        # # Label for "In Call"
        # self.call_label = Label(self.root, text="In Call! as caller", font=("Helvetica", 20, "bold"))
        # self.call_label.place(x=120, y=30)
        #
        # # Label for username
        # self.username_label = Label(self.root, text=self.label_username, font=("Helvetica", 16))
        # self.username_label.place(x=180, y=80)
        #
        # self.photo_hang_up = PhotoImage(file=r"..\images\hang_up.png").subsample(3, 3)
        # # Hang up button with icon
        # self.btn_hang_up = Button(self.root, image=self.photo_hang_up, command=self.hang_up_call,
        #                           borderwidth=0)
        # self.btn_hang_up.image = self.photo_hang_up  # keep a reference to avoid garbage collection
        # self.btn_hang_up.pack(side=LEFT, padx=20, pady=20)


    def init_panel_call_receiver(self):
        # in call
        self.call_window = self.root
        # sets the title of the
        # Toplevel widget
        self.call_who = Label(self.call_window, text="In call! as call reciever")
        self.call_who.place(x=180, y=60)

        self.audio_handling = AudioHandling(self.profile)
    def animate_handle(self):

        self.calling_image.image_id = (self.calling_image.image_id + 1) % 6
        self.calling_image.config(image=self.calling_image.image[self.calling_image.image_id // 3])
    def hang_up_call(self):
        pass

    def open_and_start_audio_channels(self):
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
    # def init_panel_destroy(self):
    #     self.call_who.destroy()
    #     self.enter_username.destroy()
    #     self.username_input_area.destroy()
    #     self.btn_contact.destroy()
    #     self.call_window.destroy()




    def wait_for_ring(self):
        pass
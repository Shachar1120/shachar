import threading
from tkinter import *
import tkinter.ttk as ttk
import os
import pyaudio
from PIL import Image, ImageTk  # ייבוא Image ו-ImageTk מ-Pillow
import sys
import socket
import pickle
from new_protocol import Pro
import select
from time import time
from pathlib import Path
from AudioHandling import AudioHandling
from call_utilities import *

class CallConnectHandling:

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

        self.images = {}
        self.move_to_in_call_acceptor = move_to_in_call_acceptor

        self.networking_obj = networking_obj

        self.transition = None
        self.state = CallStates.INIT

        self.audio_handling = None
        self.contact_name = None

        self.networking_obj.register_on_ring(self.on_ring) # for acceptor???
        self.networking_obj.register_in_call(self.in_call)
        self.networking_obj.register_on_contact(self.on_contact)

    def on_ring(self):
        self.transition = CallStates.INIT
        self.state = CallStates.RINGING # for acceptor

    def in_call(self):
        self.transition = CallStates.RINGING
        self.state = CallStates.IN_CALL

    def on_contact(self):
        self.transition = self.state
        self.state = CallStates.INIT

    def load_image(self, path, size=None):
        # פונקציה לטעינת תמונה והמרתה לפורמט Tkinter
        image = Image.open(path)
        if size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def init_panel_initiator_create(self, username): # for ringing
        #self.contacts_obj.init_panel_destroy()

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
        self.transition = CallStates.RINGING

    def destroy_panel_initiator_create(self):
        # destroies acceptor create?????
        print("in destroy 1!!!")
        self.call_who.destroy()
        self.call_who = None
        self.calling_image.destroy()
        self.calling_image = None
        self.btn_hang_up3.destroy()
        self.btn_hang_up3 = None
        print(f"type of self: {type(self)}")
        #if self.btn_hang_up is not None:
            #self.btn_hang_up.destroy()
            #self.btn_hang_up = None
        #if self.btn_answer is not None:
            #self.btn_answer.destroy()
            #self.btn_answer = None
    def init_panel_acceptor_create(self):
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
        self.btn_hang_up3 = Button(self.root, image=self.photo_hang_up, command=self.hang_up_ring,
                                  borderwidth=0)
        self.btn_hang_up3.image = self.photo_hang_up  # keep a reference to avoid garbage collection
        self.btn_hang_up3.pack(side=LEFT, padx=20, pady=20)

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
        self.call_who = None
        self.calling_image.destroy()
        self.calling_image = None
        print("btn hang up!!!", self.btn_hang_up3)
        self.btn_hang_up3.destroy()
        self.btn_hang_up3 = None
        if self.btn_answer is not None:
            self.btn_answer.destroy()
            self.btn_answer = None

    def destroy_panel_initiator_create(self):
        print("in destroy 1!!!")
        self.call_who.destroy()
        self.call_who = None
        self.calling_image.destroy()
        self.calling_image = None
        print(f"type of self: {type(self)}")
        #if self.btn_hang_up is not None:
            #self.btn_hang_up.destroy()
            #self.btn_hang_up = None
        #if self.btn_answer is not None:
            #self.btn_answer.destroy()
            #self.btn_answer = None
    def init_panel_calling(self, username=None):
        print("!2")
        print("init_panel_calling: generate AudioHandling")

        self.audio_handling = AudioHandling(self.profile)
        self.audio_handling.init_channels()

        self.root.title("In Call! as caller")
        self.contact_name = username
        # Label for "In Call"
        self.call_label = Label(self.root, text="In Call! as caller", font=("Helvetica", 20, "bold"))
        self.call_label.place(relx=0.5, rely=0.3, anchor=CENTER)  # Place label in the center top

        # Label for username
        if self.contact_name == None:
            text_calling = ""
        else:
            text_calling = f"calling {username}"
        self.username_label = Label(self.root, text=text_calling, font=("Helvetica", 16))
        self.username_label.place(relx=0.5, rely=0.4, anchor=CENTER)  # Place username label below call label

        self.photo_hang_up = PhotoImage(file=r"..\images\hang_up.png").subsample(3, 3)
        # Hang up button with icon
        self.btn_hang_up1 = Button(self.root, image=self.photo_hang_up, command=self.hang_up_call, borderwidth=0)
        self.btn_hang_up1.image = self.photo_hang_up  # keep a reference to avoid garbage collection
        self.btn_hang_up1.place(relx=0.5, rely=0.7, anchor=CENTER)  # Place button at the center bottom

    def destroy_panel_calling(self):
        #self.root.destroy()
        self.call_label.destroy()
        self.username_label.destroy()
        #self.btn_hang_up1.destroy()

    #def destroy_panel_call_reciever(self):
        #self.root.destroy()

    def hang_up_call(self):
        # self.destroy_panel_calling()
        # #self.destroy_panel_call_reciever()
        # print("exiting")
        # #os._exit(0)
        print("hung up")
        if self.audio_handling is not None:
            self.audio_handling.destroy_channels()
            self.audio_handling = None

        sending_cmd = Pro.create_msg("MOVE_TO_CONTACT".encode(), [])
        self.networking_obj.call_initiate_socket.send(sending_cmd)  # send to my socket

        #self.btn_hang_up2.destroy()
        # reject call || hangup call
        if self.state == CallStates.RINGING:
            self.transition = self.state
            self.state = CallStates.INIT

        elif self.state == CallStates.IN_CALL:
            self.transition = self.state
            self.state = CallStates.INIT



    def init_panel_call_receiver(self):
        print("!1")
        self.audio_handling = AudioHandling(self.profile)
        self.audio_handling.init_channels()
        print("init_panel_call_receiver: generate AudioHandling")
        self.transition = self.state
        self.root.title("In Call! as caller")

        # Label for "In Call"
        self.call_label = Label(self.root, text="In call! as call reciever", font=("Helvetica", 20, "bold"))
        self.call_label.place(relx=0.5, rely=0.3, anchor=CENTER)  # Place label in the center top

        # Label for username
        self.username_label = Label(self.root, font=("Helvetica", 16))
        self.username_label.place(relx=0.5, rely=0.4, anchor=CENTER)  # Place username label below call label

        self.photo_hang_up = PhotoImage(file=r"..\images\hang_up.png").subsample(3, 3)
        # Hang up button with icon
        self.btn_hang_up2 = Button(self.root, image=self.photo_hang_up, command=self.hang_up_call, borderwidth=0)
        self.btn_hang_up2.image = self.photo_hang_up  # keep a reference to avoid garbage collection
        self.btn_hang_up2.place(relx=0.5, rely=0.7, anchor=CENTER)  # Place button at the center bottom

        #self.audio_handling = AudioHandling(self.profile)
        #self.audio_handling.init_channels()
    def animate_handle(self):

        if self.calling_image is not None:
            self.calling_image.image_id = (self.calling_image.image_id + 1) % 6
            self.calling_image.config(image=self.calling_image.image[self.calling_image.image_id // 3])
    def hang_up_ring(self):
        if self.audio_handling is not None:
            self.audio_handling.destroy_channels()
            self.audio_handling = None

        # Destroy GUI elements
        # if self.state == CallStates.RINGING: # reject call
        #     pass
        #     #self.destroy_panel_initiator_create()
        # elif self.state == CallStates.IN_CALL: # hangup call
        #     if self.profile.caller:
        #         self.destroy_panel_calling()
        #     else:
        #         self.destroy_panel_acceptor_create()
        sending_cmd = Pro.create_msg("MOVE_TO_CONTACT".encode(), [])
        self.networking_obj.call_initiate_socket.send(sending_cmd)  # send to my socke

        self.btn_hang_up3.destroy()
        self.btn_answer.destroy()
        # reject call || hangup call
        if self.state == CallStates.RINGING:
            self.transition = self.state
            self.state = CallStates.INIT

        elif self.state == CallStates.IN_CALL:
            self.transition = self.state
            self.state = CallStates.INIT


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





    def wait_for_ring(self):
        pass

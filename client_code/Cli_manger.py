

import socket
import threading
from tkinter import *  # ייבוא כל הפונקציות והמחלקות מ-tkinter
from PIL import Image, ImageTk  # ייבוא Image ו-ImageTk מ-Pillow
import pyaudio
from RegisterPanel import RegisterPanel
from AssignPanel import AssignPanel
from ContactsPanel import ContactsPanel, ButtonItem
from CallConnectHandling import CallConnectHandling
from new_protocol import Pro
from call_utilities import *
from NetworkHandling import NetworkHandling
#from DataBase import DataBase
#import sqlite3
#import mysql.connector

class Cli:
    def __init__(self, profile):
        # open socket with the server
        self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.profile = profile
        self.root = Tk()
        self.user1 = None
        self.username1 = None
        # sets the geometry of main
        # root window
        self.root.geometry("600x400")
        self.root.title("Home Page")

        #self.database_obj = DataBase()

        self.networking_obj = NetworkHandling(self.socket_to_server, self.profile, self.move_to_ringing_acceptor)


        self.register_obj = RegisterPanel(self.root,
                                          self.socket_to_server,
                                          self.RegisterComplete,
                                          self.profile.call_accept_port)
        self.assign_obj = AssignPanel(self.root,
                                      self.socket_to_server,
                                      self.AssignComplete)

        self.call_obj = CallConnectHandling(self.root,
                                            self.socket_to_server,
                                            self.ContactsComplete,
                                            self.profile,
                                            self.networking_obj,

                                            self.move_to_in_call_acceptor)
        self.contacts_obj = ContactsPanel(self.root,
                                          self.socket_to_server,
                                          self.ContactsComplete,
                                          self.move_to_ringing_initiator,
                                          self.profile,
                                          self.networking_obj, self.assign_obj, self.register_obj)
        self.networking_obj.init_network(self.contacts_obj)
        self.images = {}
        self.init_images_dict()

        self.init_panel_create()


    def init_panel_create(self):

        # יצירת תווית והצבת התמונה הראשית בתוכה
        self.main_image_label = Label(self.root, image=self.images['main_image'])
        self.main_image_label.pack(pady=20)  # הצבת התמונה במרכז עם מרווח מעל ומתחת

        # יצירת מסגרת עבור הכפתורים
        self.button_frame = Frame(self.root)
        self.button_frame.pack(pady=10)  # הצבת המסגרת עם מרווח מתחת

        # יצירת כפתורים והצבתם במסגרת, הסתרת המסגרת כך שהתמונות יראו כחלק מהמסך
        self.button_register = Button(self.button_frame, image=self.images['register_button_image'], command=self.move_to_register, bd=0)
        self.button_register.pack(side=LEFT, padx=10)  # הצבת הכפתור הראשון עם מרווח מימין

        self.button_assign = Button(self.button_frame, image=self.images['login_button_image'], command=self.move_to_assign, bd=0)
        self.button_assign.pack(side=LEFT, padx=10)  # הצבת הכפתור השני עם מרווח מימין

    def init_images_dict(self):
        # נתיבים לתמונות
        main_image_path = r"..\images\logo VOW1.png"
        register_button_image_path = r"..\images\register icon1.png"
        login_button_image_path = r"..\images\log in icon1.png"

        # טעינת התמונות ושמירתם במילון
        self.images['main_image'] = self.load_image(main_image_path, (250, 224))
        self.images['register_button_image'] = self.load_image(register_button_image_path)
        self.images['login_button_image'] = self.load_image(login_button_image_path)


    def load_image(self, path, size=None):
        # פונקציה לטעינת תמונה והמרתה לפורמט Tkinter
        image = Image.open(path)
        if size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def RegisterComplete(self):
        self.register_obj.init_panel_destroy()
        self.init_panel_create()

    def AssignComplete(self):
        self.assign_obj.init_panel_destroy()
        # destroy main:
        self.destroy_enter_panel()

        # start call based networking

        # יצירת תהליך חדש שמחכה לפתיחת שיחה
        thread = threading.Thread(target=self.networking_obj.wait_for_network)

        # הפעלת התהליך
        thread.start()

        self.user1 = self.assign_obj.user1
        self.contacts_obj.init_panel_create(self.user1)

    def ContactsComplete(self):
        self.contacts_obj.init_panel_destroy()


    def CallComplete(self):
        pass

    def move_to_register(self):
        self.destroy_enter_panel()
        #self.register_obj = RegisterPanel(self.root, self.socket_to_server, self.RegisterComplete, self.profile.call_accept_port)
        self.register_obj.init_panel_create()

    def move_to_assign(self):
        self.destroy_enter_panel()
        #self.assign_obj = AssignPanel(self.root, self.socket_to_server, self.AssignComplete)
        self.assign_obj.init_panel_create()

    def move_to_ringing_initiator(self, username):
        self.contacts_obj.init_panel_destroy()
        self.call_obj.init_panel_initiator_create(username)
        #self.call_obj.init_panel_acceptor_create()
        print("moved to ringing as initiator!!")

    def move_to_ringing_acceptor(self):
        self.contacts_obj.init_panel_destroy()
        self.call_obj.init_panel_acceptor_create()
        print("moved to ringing as acceptor!!")


    def move_to_in_call_initiator(self):
        print("in destroy!!!")
        self.call_obj.destroy_panel_initiator_create()
        self.call_obj.transition = CallStates.IN_CALL
        self.call_obj.init_panel_calling(self.username1)

    def move_to_in_call_acceptor(self):
        self.call_obj.state = CallStates.IN_CALL

        cmd = Pro.cmds[Pro.IN_CALL]
        # send IN_CALL message to the caller = CALL ACK
        try:
            sending_cmd = Pro.create_msg(cmd.encode(), [])
            self.networking_obj.call_initiate_socket.send(sending_cmd)  # send to my socket
            print("IN_CALL message sent successfully")
        except Exception as e:
            print(f"Failed to send IN_CALL message: {e}")



        self.call_obj.destroy_panel_acceptor_create()
        self.call_obj.init_panel_call_receiver()
        if self.call_obj.audio_handling is not None:
            self.networking_obj.set_audio_handler(self.call_obj.audio_handling)
        else:
            print("missing audio handler!!!")



        # then react to it

    def destroy_enter_panel(self):
        self.button_register.destroy()
        self.button_assign.destroy()
        self.main_image_label.destroy()
        self.button_frame.destroy()




    def move_from_call_to_contact_list(self):
        self.call_obj.destroy_panel_calling()
        self.call_obj.transition = CallStates.INIT
        self.contacts_obj.init_panel_create()

    def move_from_ringing_to_contact_list(self):
        print('move_from_ringing_to_contact_list!!!')
        self.call_obj.destroy_panel_initiator_create()
        self.call_obj.transition = CallStates.INIT
        self.contacts_obj.init_panel_create()



    #def hang_up_call(self):
        #pass


    # def select_microphone(self, index, p):
    #     # כנראה שלא משתמשת בפונקציה!!
    #     # Select a microphone with a specific index
    #     print(f"please select a microphone")
    #     # Get the device info
    #     device_info = p.get_device_info_by_index(index)
    #     # Check if this device is a microphone (an input device)
    #     if device_info.get('maxInputChannels') > 0:
    #         print(f"Selected Microphone: {device_info.get('name')}")
    #         return device_info.get('name')
    #     else:
    #         print(f"No microphone at index {index}")
    #
    # def list_microphones(self, devices, p):
    #     # כנראה שלא משתמשת בפונקציה!!
    #     # Iterate through all devices
    #     for i in range(devices):
    #         # Get the device info
    #         device_info = p.get_device_info_by_index(i)
    #         # Check if this device is a microphone (an input device)
    #         if device_info.get('maxInputChannels') > 0:
    #             print(f"Microphone: {device_info.get('name')} , Device Index: {device_info.get('index')}")


    def connect(self, ip, port):
        self.socket_to_server.connect((ip, port))

    # tkintern:

    def main_loop(self):
        self.root.after(40, self.check_network_answers)
        self.root.mainloop()

    def check_network_answers(self):
        if CallStates.RINGING == self.call_obj.state and self.call_obj is not None:
            self.call_obj.animate_handle()

        # בגלל שפתחנו thread נוסף אז הגוי לא מציג אותו, בניגוד לmake_ring שזה הthread הראשי
        # נעשה פונקציה שכל 40 מילי שניות תעדכן את המסך
        if self.call_obj.transition != self.call_obj.state:
            if CallStates.RINGING == self.call_obj.state:
                self.move_to_ringing_acceptor()
                #self.move_to_ringing()
                self.call_obj.transition = self.call_obj.state

            if CallStates.IN_CALL == self.call_obj.state:
                self.move_to_in_call_initiator()
                self.call_obj.transition = self.call_obj.state

            if CallStates.INIT == self.call_obj.state:
                if self.call_obj.transition == CallStates.RINGING:
                    print("from ringing to contacts!!!!")
                    self.move_from_ringing_to_contact_list()

                elif self.call_obj.transition == CallStates.IN_CALL:
                    self.move_from_call_to_contact_list()
                self.call_obj.transition = self.call_obj.state

        self.root.after(40, self.check_network_answers)

def Main():
    print("1: for 2001, 2: for 2002")
    profiles = [ UserProfile(2001, 2002, 0, 15 ), UserProfile(2002, 2001, 0, 18)]
    print("input 1 or 2 to choose user profile")
    whoami = int(input())
    #if whoami== 1: #profile1 = profiles[0]

    myclient = Cli(profiles[whoami-1]) # if I write 2 -profiles[1], and if I write 1-profiles[0]
    myclient.connect("127.0.0.1", Pro.PORT)
    myclient.main_loop()


if __name__ == "__main__":
    Main()
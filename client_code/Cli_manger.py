

import socket
import threading
from tkinter import *  # ייבוא כל הפונקציות והמחלקות מ-tkinter
from PIL import Image, ImageTk  # ייבוא Image ו-ImageTk מ-Pillow
import pyaudio
from RegisterPanel import RegisterPanel
from AssignPanel import AssignPanel
from ContactsPanel import ContactsPanel
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
        self.server_ip = '127.0.0.1'
        self.call_port = "2001"
        self.root = Tk()

        # sets the geometry of main
        # root window
        self.root.geometry("600x400")
        self.root.title("Home Page")

        #self.database_obj = DataBase()

        self.networking_obj = NetworkHandling(self.socket_to_server, self.profile, self.move_to_ringing_acceptor, self.call_port)
        self.networking_obj.init_network()

        self.register_obj = RegisterPanel(self.root,
                                          self.socket_to_server,
                                          self.RegisterComplete,
                                          self.profile.call_accept_port, self.server_ip)
        self.assign_obj = AssignPanel(self.root,
                                      self.socket_to_server,
                                      self.AssignComplete, self.server_ip, self.call_port)

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
                                          self.networking_obj)
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

        self.info_frame = Frame(self.root)
        self.info_frame.pack(pady=10)

        # הוספת תווית, שדה מידע וכפתור עבור server IP
        self.server_ip_label = Label(self.info_frame, text="Server IP:", width=10)
        self.server_ip_label.pack(side=LEFT, padx=5)

        self.server_ip_entry = Entry(self.info_frame, width=15)
        self.server_ip_entry.insert(0, "127.0.0.1")
        self.server_ip_entry.pack(side=LEFT, padx=5)

        self.server_ip_submit = Button(self.info_frame, text="Submit", command=self.submit_server_ip, width=8, height=1,
                                       bd=1, highlightthickness=0)
        self.server_ip_submit.pack(side=LEFT, padx=5)

        # הוספת תווית, שדה מידע וכפתור עבור call port
        self.call_port_label = Label(self.info_frame, text="Call Port:", width=10)
        self.call_port_label.pack(side=LEFT, padx=5)

        self.call_port_entry = Entry(self.info_frame, width=15)
        self.call_port_entry.insert(0, "2001")
        self.call_port_entry.pack(side=LEFT, padx=5)

        self.call_port_submit = Button(self.info_frame, text="Submit", command=self.submit_call_port, width=8, height=1,
                                       bd=1, highlightthickness=0)
        self.call_port_submit.pack(side=LEFT, padx=5)

    def init_images_dict(self):
        # נתיבים לתמונות
        main_image_path = r"..\images\logo VOW1.png"
        register_button_image_path = r"..\images\register icon1.png"
        login_button_image_path = r"..\images\log in icon1.png"

        # טעינת התמונות ושמירתם במילון
        self.images['main_image'] = self.load_image(main_image_path, (250, 224))
        self.images['register_button_image'] = self.load_image(register_button_image_path)
        self.images['login_button_image'] = self.load_image(login_button_image_path)

    def submit_server_ip(self):
        # פעולה לביצוע בעת לחיצה על כפתור 'Submit' של 'Server IP'
        self.server_ip = self.server_ip_entry.get()
        print(f"Submitted Server IP: {self.server_ip}")

    def submit_call_port(self):
        # פעולה לביצוע בעת לחיצה על כפתור 'Submit' של 'Call Port'
        call_port = self.call_port_entry.get()
        print(f"Submitted Call Port: {call_port}")
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

        self.contacts_obj.init_panel_create()

    def ContactsComplete(self):
        self.contacts_obj.init_panel_destroy()


    def CallComplete(self):
        pass

    def move_to_register(self):
        self.destroy_enter_panel()
        self.register_obj = RegisterPanel(self.root, self.socket_to_server, self.RegisterComplete, self.profile.call_accept_port, self.server_ip)
        self.register_obj.init_panel_create()

    def move_to_assign(self):
        self.destroy_enter_panel()
        self.assign_obj = AssignPanel(self.root, self.socket_to_server, self.AssignComplete, self.server_ip, self.call_port)
        self.assign_obj.init_panel_create()

    def move_to_ringing_initiator(self):
        self.contacts_obj.init_panel_destroy()
        self.call_obj.init_panel_initiator_create()
        #self.call_obj.init_panel_acceptor_create()
        print("moved to ringing as initiator!!")

    def move_to_ringing_acceptor(self):
        self.contacts_obj.init_panel_destroy()
        self.call_obj.init_panel_acceptor_create()
        print("moved to ringing as acceptor!!")


    def move_to_in_call_initiator(self):

        self.call_obj.destroy_panel_initiator_create()
        self.call_obj.state = CallConnectHandling.IN_CALL
        self.call_obj.init_panel_calling(self.contacts_obj.username)

    def move_to_in_call_acceptor(self):
        self.call_obj.state = CallConnectHandling.IN_CALL

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
        self.info_frame.destroy()
        self.server_ip_label.destroy()
        self.server_ip_entry.destroy()
        self.server_ip_submit.destroy()
        self.call_port_label.destroy()
        self.call_port_entry.destroy()
        self.call_port_submit.destroy()



    def hang_up_call(self):
        pass


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
        # בגלל שפתחנו thread נוסף אז הגוי לא מציג אותו, בניגוד לmake_ring שזה הthread הראשי
        # נעשה פונקציה שכל 40 מילי שניות תעדכן את המסך
        if CallStates.RINGING == self.call_obj.state:
            if self.call_obj.transition: #is True
                self.move_to_ringing_acceptor()
                #self.move_to_ringing()
                self.call_obj.transition = False


            self.call_obj.animate_handle()

        if CallStates.IN_CALL == self.call_obj.state:
            if self.call_obj.transition:
                self.move_to_in_call_initiator()
                self.call_obj.transition = False

        self.root.after(40, self.check_network_answers)

def Main():
    #print("1: for 2001, 2: for 2002")
    profiles = [ UserProfile(2001, 2002, 0, 15 ), UserProfile(2002, 2001, 0, 18)]

    #if whoami== 1: #profile1 = profiles[0]

    myclient = Cli(profiles[0]) # if I write 2 -profiles[1], and if I write 1-profiles[0]
    #myclient.connect("127.0.0.1", Pro.PORT)
    #myclient.connect(myclient.server_ip, Pro.PORT)
    myclient.main_loop()


if __name__ == "__main__":
    Main()

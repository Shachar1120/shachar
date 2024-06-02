
import socket
from tkinter import *  # ייבוא כל הפונקציות והמחלקות מ-tkinter
from PIL import Image, ImageTk  # ייבוא Image ו-ImageTk מ-Pillow
import pyaudio
from RegisterPanel import RegisterPanel
from AssignPanel import AssignPanel
from ContactsPanel import ContactsPanel
from CallConnectHandling import CallConnectHandling
from new_protocol import Pro
from call_utilities import *

class Cli:
    def __init__(self, profile):
        # open socket with the server
        self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        call_initiate_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.profile = profile
        # self.assigned_client_details = {}  # Create the dictionary globally

        self.root = Tk()

        # sets the geometry of main
        # root window
        self.root.geometry("600x400")
        self.root.title("Home Page")

        self.register_obj = RegisterPanel(self.root,
                                          self.socket_to_server,
                                          self.RegisterComplete,
                                          self.profile.call_accept_port)
        self.assign_obj = AssignPanel(self.root,
                                      self.socket_to_server,
                                      self.AssignComplete)
        # sending root for socket_to_server and root

        self.call_obj = CallConnectHandling(self.root, self.socket_to_server, self.ContactsComplete, self.profile, call_initiate_socket)
        self.contacts_obj = ContactsPanel(self.root,
                                          self.socket_to_server,
                                          self.ContactsComplete,
                                          self.move_to_ringing_initiator,
                                          self.profile,
                                          call_initiate_socket)
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

    # def send_cmd(self, cmd: bytes, params):
    #     msg_to_send = Pro.create_msg(cmd, params)
    #     self.socket_to_server.send(msg_to_send)

    # def get_response(self):
    #     res, message = Pro.get_msg(self.socket_to_server)
    #     message = message.decode()
    #     if not res:
    #         return False, message
    #     return True, message

    # def get_response_from_other_client(self):
    #     try:
    #         # Attempt to receive a message using Pro.get_msg
    #         res, message = Pro.get_msg(self.contacts_obj.call_initiate_socket)
    #         message = message.decode()
    #         print(f"Response: {res}, Message: {message}")
    #
    #         if not res:
    #             print(f"Failed to receive message. Response: {res}")
    #             return False, message
    #
    #         print(f"Successfully received message: {message}")
    #         return True, message
    #
    #     except socket.timeout:
    #         print("Socket timed out while waiting for a response.")
    #         return False, "Socket timeout"
    #
    #     except socket.error as e:
    #         print(f"Socket error occurred: {e}")
    #         return False, f"Socket error: {e}"
    #
    #     except Exception as e:
    #         print(f"An unexpected error occurred: {e}")
    #         return False, f"Unexpected error: {e}"

    # def check_if_pickle(self, msg):
    #     try:
    #         # Try to unpickle the message
    #         pickle.loads(msg)
    #         # If successful, the message is in pickle format
    #         return True
    #     except pickle.UnpicklingError:
    #         # If unsuccessful, the message is not in pickle format
    #         return False

    # def split_message(self, message):
    #     message_parts = message.split(Pro.PARAMETERS_DELIMITER.encode())  # message: cmd + len(params) + params
    #     opcode = message_parts[0].decode()
    #     nof_params = int(message_parts[1].decode())
    #     params = message_parts[2:]
    #     return opcode, nof_params, params

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
        self.contacts_obj.init_panel_create()

    def ContactsComplete(self):
        self.contacts_obj.init_panel_destroy()
        self.call_obj.init_panel_create_ringing()

    def CallComplete(self):
        pass

    def move_to_register(self):
        self.destroy_enter_panel()
        self.register_obj = RegisterPanel(self.root, self.socket_to_server, self.RegisterComplete, self.profile.call_accept_port)
        self.register_obj.init_panel_create()

    def move_to_assign(self):
        self.destroy_enter_panel()
        self.assign_obj = AssignPanel(self.root, self.socket_to_server, self.AssignComplete)
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

    # def move_to_ring_receiving(self):
    #     self.contacts_obj.init_panel_destroy()
    #     self.init_panel_create_ring_reciving()
    #     print("moved to ring receiving!!")

    def move_to_calling(self):
        self.destroy_panel_ringing()
        self.init_panel_calling()

    def move_to_call_receiving(self):
        self.contacts_obj.state = ContactsPanel.IN_CALL

        cmd = Pro.cmds[Pro.IN_CALL]
        # send IN_CALL message to the caller = CALL ACK
        try:
            sending_cmd = Pro.create_msg(cmd.encode(), [])
            self.contacts_obj.call_initiate_socket.send(sending_cmd)  # send to my socket
            print("IN_CALL message sent successfully")
        except Exception as e:
            print(f"Failed to send IN_CALL message: {e}")


        self.destroy_panel_ring_receiver()
        self.init_panel_call_receiver()


        # then react to it

    def destroy_enter_panel(self):
        self.button_register.destroy()
        self.button_assign.destroy()
        self.main_image_label.destroy()
        self.button_frame.destroy()

    def init_panel_create_ringing(self):
        self.ringing_window = self.root
        self.ringing_window.title("Log In")

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
        self.calling_image = Label(self.ringing_window, image=button_array[0])
        self.calling_image.place(x=200, y=100)
        self.calling_image.image = button_array
        self.calling_image.image_id = 0

        self.contacts_obj.state = CallStates.RINGING
        self.contacts_obj.transition = True


    def check_if_got_msg(self):
        try:
            # Attempt to receive a message using Pro.get_msg
            res, message = Pro.get_msg(self.contacts_obj.call_initiate_socket)
            message = message.decode()
            print(f"Response: {res}, Message: {message}")

            if not res:
                print(f"Failed to receive message. Response: {res}")
                return False, message

            print(f"Successfully received message: {message}")
            return True, message

        except socket.timeout:
            print("Socket timed out while waiting for a response.")
            return False, "Socket timeout"

        except socket.error as e:
            print(f"Socket error occurred: {e}")
            return False, f"Socket error: {e}"

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False, f"Unexpected error: {e}"


    def init_panel_create_ring_reciving(self):
        self.ringing_window = self.root
        # # sets the title of the
        # # Toplevel widget
        # self.ringing_window.title("Someone is ringing")
        #
        # self.call_who = Label(self.ringing_window, text="Someone is ringing")
        # self.call_who.place(x=180, y=60)



        # Create a Button
        photo = PhotoImage(file=r"..\images\ring1.png")
        photoimage1 = photo.subsample(3, 3)
        photo = PhotoImage(file=r"..\images\ring2.png")
        photoimage2 = photo.subsample(3, 3)
        photo = PhotoImage(file=r"..\images\ringing1.png")
        photoimage3 = photo.subsample(3, 3)

        button_array = [photoimage1, photoimage2, photoimage3]
        self.btn_calling = Label(self.ringing_window, image=button_array[0])
        self.btn_calling.place(x=200, y=100)
        self.btn_calling.image = button_array
        self.btn_calling.image_id = 0




        # self.call_who = Label(self.ringing_window, text="... is calling")
        # self.call_who.pack(pady=20)
        #
        # self.ringing_window.title("Incoming Call")
        #
        # self.photo_answer = PhotoImage(file=r"..\images\answer.png").subsample(3, 3)
        # self.photo_hang_up = PhotoImage(file=r"..\images\hang_up.png").subsample(3, 3)
        #
        # # Create buttons
        # self.btn_hang_up = Button(self.ringing_window, image=self.photo_hang_up, command=self.hang_up_call,
        #                           borderwidth=0)
        # self.btn_hang_up.image = self.photo_hang_up  # keep a reference to avoid garbage collection
        # self.btn_hang_up.pack(side=LEFT, padx=20, pady=20)
        #
        # self.btn_answer = Button(self.ringing_window, image=self.photo_answer, command=self.move_to_call_receiving,
        #                          borderwidth=0)
        # self.btn_answer.image = self.photo_answer  # keep a reference to avoid garbage collection
        # self.btn_answer.pack(side=RIGHT, padx=10, pady=20)

    def init_answer_and_hangup_buttons(self):

        print("moved to init_answer_and_hangup_buttons!!!")
        # sets the title of the
        # Toplevel widget
        self.ringing_window.title("Someone is ringing")

        self.call_who = Label(self.ringing_window, text="Someone is ringing")
        self.call_who.place(x=180, y=60)
        self.call_who = Label(self.ringing_window, text="... is calling")
        self.call_who.pack(pady=20)

        self.ringing_window.title("Incoming Call")

        self.photo_answer = PhotoImage(file=r"..\images\answer.png").subsample(3, 3)
        self.photo_hang_up = PhotoImage(file=r"..\images\hang_up.png").subsample(3, 3)

        # Create buttons
        self.btn_hang_up = Button(self.ringing_window, image=self.photo_hang_up, command=self.hang_up_call,
                                  borderwidth=0)
        self.btn_hang_up.image = self.photo_hang_up  # keep a reference to avoid garbage collection
        self.btn_hang_up.pack(side=LEFT, padx=20, pady=20)

        self.btn_answer = Button(self.ringing_window, image=self.photo_answer, command=self.move_to_call_receiving,
                                 borderwidth=0)
        self.btn_answer.image = self.photo_answer  # keep a reference to avoid garbage collection
        self.btn_answer.pack(side=RIGHT, padx=10, pady=20)


    def destroy_panel_ringing(self):
        self.call_who.destroy()
        #self.image_label.destroy()
        #self.image_label = None
        self.btn_calling1.destroy()

    def destroy_panel_ring_receiver(self):

        self.call_who.destroy()
        self.btn_calling.destroy()



    def hang_up_call(self):
        pass
    def init_panel_calling(self):
        self.call_window = self.root
        # sets the title of the
        # Toplevel widget
        self.call_label = Label(self.ringing_window, text="In call! as caller")
        self.call_label.place(x=180, y=60)

    def select_microphone(self, index, p):
        # Select a microphone with a specific index
        print(f"please select a microphone")
        # Get the device info
        device_info = p.get_device_info_by_index(index)
        # Check if this device is a microphone (an input device)
        if device_info.get('maxInputChannels') > 0:
            print(f"Selected Microphone: {device_info.get('name')}")
            return device_info.get('name')
        else:
            print(f"No microphone at index {index}")

    def list_microphones(self, devices, p):
        # Iterate through all devices
        for i in range(devices):
            # Get the device info
            device_info = p.get_device_info_by_index(i)
            # Check if this device is a microphone (an input device)
            if device_info.get('maxInputChannels') > 0:
                print(f"Microphone: {device_info.get('name')} , Device Index: {device_info.get('index')}")
    def call_transmit(self):

        # read audio and send
        sound = True
        CHUNK = 4096
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 10

        p = pyaudio.PyAudio()
        stream_input = p.open(format=FORMAT,
                              channels=CHANNELS,
                              rate=RATE,
                              input=True,
                              input_device_index=self.profile.my_mic,
                              frames_per_buffer=CHUNK)
        stream_output = p.open(format=FORMAT,
                               channels=CHANNELS,
                               rate=RATE,
                               output=True,  # for speaker
                               input_device_index=self.profile.my_speaker,
                               frames_per_buffer=CHUNK)

        while True:
            data = stream_input.read(CHUNK)

            cmd = Pro.cmds[Pro.FRAME].encode()
            #params = [pickle.dumps(data)]
            params = [data]
            msg_to_send = Pro.create_msg(cmd, params)
            self.contacts_obj.call_initiate_socket.send(msg_to_send)


        p.terminate()

    def init_panel_call_receiver(self):
        # in call
        self.call_window = self.root
        # sets the title of the
        # Toplevel widget
        self.call_who = Label(self.ringing_window, text="In call! as call reciever")
        self.call_who.place(x=180, y=60)

        thread = threading.Thread(target=self.call_transmit).start()

    def connect(self, ip, port):
        self.socket_to_server.connect((ip, port))

    # tkintern:

    def main_loop(self):
        self.root.after(40, self.check_network_answers)
        self.root.mainloop()

    def check_network_answers(self):
        # בגלל שפתחנו thread נוסף אז הגוי לא מציג אותו, בניגוד לmake_ring שזה הthread הראשי
        # נעשה פונקציה שכל 40 מילי שניות תעדכן את המסך
        if CallStates.RINGING == self.contacts_obj.state:
            if self.contacts_obj.transition:
                self.move_to_ringing_acceptor()
                #self.move_to_ringing()
                self.contacts_obj.transition = False


            self.call_obj.animate_handle()

        if CallStates.IN_CALL == self.contacts_obj.state:
            if self.contacts_obj.transition:
                self.move_to_calling()
                self.contacts_obj.transition = False

        self.root.after(40, self.check_network_answers)

def Main():
    print("1: for 2001, 2: for 2002")
    profiles = [ UserProfile(2001, 2002, 0, 18 ), UserProfile(2002, 2001, 0, 18)]
    print("input 1 or 2 to choose user profile")
    whoami = int(input())
    #if whoami== 1: #profile1 = profiles[0]

    myclient = Cli(profiles[whoami-1]) # if I write 2 -profiles[1], and if I write 1-profiles[0]
    myclient.connect("127.0.0.1", Pro.PORT)
    myclient.main_loop()


if __name__ == "__main__":
    Main()
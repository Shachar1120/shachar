from tkinter_update import *
import socket
from tkinter import *  # ייבוא כל הפונקציות והמחלקות מ-tkinter
from PIL import Image, ImageTk  # ייבוא Image ו-ImageTk מ-Pillow


class Cli:
    def __init__(self, my_port, your_port):
        # open socket with the server
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_port = my_port
        self.connect_port = your_port
        # self.assigned_client_details = {}  # Create the dictionary globally
        self.images = {}

        self.root = Tk()

        # sets the geometry of main
        # root window
        self.root.geometry("600x400")
        self.root.title("Home Page")
        self.init_panel_create()


    def send_cmd(self, cmd: bytes, params):
        msg_to_send = Pro.create_msg(cmd, params)
        self.my_socket.send(msg_to_send)

    def get_response(self):
        res, message = Pro.get_msg(self.my_socket)
        if not res:
            return False, message
        return True, message

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
        #self.contacts_obj.init_panel_destroy()
        self.call_obj.init_panel_create_calling()

    def CallComplete(self):
        pass

    def move_to_register(self):
        self.destroy_enter_panel()
        self.register_obj = RegisterPanel(self.root, self.my_socket, self.RegisterComplete, self.server_port)
        self.register_obj.init_panel_create()

    def move_to_assign(self):
        self.destroy_enter_panel()
        self.assign_obj = AssignPanel(self.root, self.my_socket, self.AssignComplete)
        self.assign_obj.init_panel_create()





    def init_panel_create(self):

        self.register_obj = RegisterPanel(self.root, self.my_socket, self.RegisterComplete, self.server_port)
        self.assign_obj = AssignPanel(self.root, self.my_socket, self.AssignComplete)
        # sending root for my_socket and root
        self.contacts_obj = ContactsPanel(self.root, self.my_socket, self.ContactsComplete, self.move_to_calling, self.move_to_call_receiving, self.server_port, self.connect_port )
        self.call_obj = CallConnectHandling(self.root, self.my_socket, self.CallComplete)

        # נתיבים לתמונות
        main_image_path = r"C:\סייבר\project\shachar-master\images\logo VOW1.png"
        register_button_image_path = r"C:\סייבר\project\shachar-master\images\register icon1.png"
        login_button_image_path = r"C:\סייבר\project\shachar-master\images\log in icon1.png"

        # טעינת התמונות ושמירתם במילון
        self.images['main_image'] = self.load_image(main_image_path, (250, 224))
        self.images['register_button_image'] = self.load_image(register_button_image_path)
        self.images['login_button_image'] = self.load_image(login_button_image_path)

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

        #############
        #self.welcome_label = Label(self.root, text="Welcome to VidPal!")
        #self.welcome_label.place(x=40, y=50)


        # Import the image using PhotoImage function
        #click_btn = PhotoImage(file=r"..\images\register icon.png")

        # Let us create a label for button event
        #img_label = Label(image=click_btn)
        # Let us create a dummy button and pass the image
        #button = Button(self.root, image=click_btn, command=self.move_to_register,
                        #borderwidth=0)
        #button.pack(pady=30)
        # Create a Button
        #self.btn_reg = Button(self.root, image=click_btn, command=self.move_to_register)
        #self.btn_reg.place(x=30, y=100)

        # Create a Button
        #self.btn_assign = Button(self.root, text='Log In', command=self.move_to_assign)
        #self.btn_assign.place(x=200, y=100)


    def destroy_enter_panel(self):
        self.button_register.destroy()
        self.button_assign.destroy()
        self.main_image_label.destroy()
    def move_to_calling(self):
        self.contacts_obj.init_panel_destroy()
        self.init_panel_create_calling()
        print("moved to call!!")

    def move_to_call_receiving(self):
        self.contacts_obj.init_panel_destroy()
        self.init_panel_create_call_reciving()
        print("moved to call!!")


    def init_panel_create_calling(self):
        self.ringing_window = self.root
        # sets the title of the
        # Toplevel widget
        self.ringing_window.title("I am calling")

        self.call_who = Label(self.ringing_window, text="I am calling")
        self.call_who.place(x=180, y=60)



    def init_panel_create_call_reciving(self):
        self.ringing_window = self.root
        # sets the title of the
        # Toplevel widget
        self.ringing_window.title("Someone is calling")

        self.call_who = Label(self.ringing_window, text="Someone is calling")
        self.call_who.place(x=180, y=60)


        # Create a Button
        photo = PhotoImage(file=r"..\images\ringing1.png")
        photoimage1 = photo.subsample(3, 3)
        photo = PhotoImage(file=r"..\images\ringing2.png")
        photoimage2 = photo.subsample(3, 3)
        photo = PhotoImage(file=r"..\images\ringing1.png")
        photoimage3 = photo.subsample(3, 3)

        button_array = [photoimage1, photoimage2, photoimage3]
        self.btn_calling = Button(self.ringing_window, image=button_array[0], command=self.move_to_register)
        self.btn_calling.place(x=200, y=100)
        self.btn_calling.image = button_array
        self.btn_calling.image_id = 0


    def connect(self, ip, port):
        self.my_socket.connect((ip, port))

    # tkintern:

    def main_loop(self):
        self.root.after(40, self.check_network_answers)
        self.root.mainloop()

    def check_network_answers(self):
        # בגלל שפתחנו thread נוסף אז הגוי לא מציג אותו, בניגוד לmake_call שזה הthread הראשי
        # נעשה פונקציה שכל 40 מילי שניות תעדכן את המסך
        if ContactsPanel.RINGING == self.contacts_obj.state:
            if self.contacts_obj.transition:
                self.move_to_call_receiving()
                self.contacts_obj.transition = False

            self.btn_calling.image_id = (self.btn_calling.image_id + 1) % 6
            self.btn_calling.config(image=self.btn_calling.image[self.btn_calling.image_id//3])


        self.root.after(40, self.check_network_answers)


def Main():
    print("1: for 2001, 2: for 2002")
    if int(input()) == 1:
        my_port = 2001
        your_port = 2002

    else:
        my_port = 2002
        your_port = 2001
    myclient = Cli(my_port, your_port)
    myclient.connect("127.0.0.1", Pro.PORT)
    myclient.main_loop()


if __name__ == "__main__":
    Main()

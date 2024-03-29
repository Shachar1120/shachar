from tkinter import *
from tkinter.ttk import *
import socket
import pickle
from new_protocol import Pro


class AssignPanel:
    def __init__(self, root, my_socket):

        self.panel_window = None
        self.my_socket = my_socket

    #?????
    def send_cmd(self, cmd: bytes, params):
        msg_to_send = Pro.create_msg(cmd, params)
        self.my_socket.send(msg_to_send)

    def init_panel_create(self):
        # Toplevel object which will
        # be treated as a new window

        self.panel_window = Toplevel(self)
        # sets the title of the
        # Toplevel widget
        self.panel_window.title("Log In")

        # sets the geometry of toplevel
        self.panel_window.geometry("450x300")

        # the label for user_name
        self.user_name = Label(self.panel_window, text="Username")
        self.user_name.place(x=40, y=60)

        # the label for user_password
        self.user_password = Label(self.panel_window, text="Password")
        self.user_password.place(x=40, y=100)

        self.user_name_input_area = Entry(self.panel_window, width=30)
        self.user_name_input_area.place(x=110, y=60)

        self.user_password_entry_area = Entry(self.panel_window, width=30)
        self.user_password_entry_area.place(x=110, y=100)

        self.submit_button = Button(self.panel_window, text="Submit", command=self.submit_assign)
        self.submit_button.place(x=40, y=130)

    def init_panel_destroy(self):
        self.submit_button.destroy()
        self.user_password_entry_area.destroy()
        self.user_name_input_area.destroy()
        self.user_password.destroy()
        self.user_name.destroy()
        if hasattr(self, 'try_again_label') and self.try_again_label1:
            # Assign not succeeded!!
            self.try_again_label1 = None
            self.try_again_label1.pack()
        self.panel_window.destroy()
        self.panel_window = None

    def submit_assign(self, newWindow):

        # hasattr is a python function that checks if a value exists

        #if hasattr(self, 'try_again_label'):
        #    self.try_again_label.destroy()

        #if hasattr(self, 'try_again_label1'):
        #    self.try_again_label.destroy()

        cmd = "ASSIGN"
        username = self.user_name_input_area.get()
        password = self.user_password_entry_area.get()

        # Check if username and password are not empty
        if username.strip() and password.strip():
            print("the params:", username, password)

            params = [username.encode(), password.encode()]
            if not Pro.check_cmd_and_params(cmd, params):
                if not hasattr(self, 'try_again_label') or not self.try_again_label1:
                    # Assign not succeeded!!
                    self.try_again_label1 = Label(newWindow, text="Couldn't Log In! Try Again.")
                    self.try_again_label1.pack()

            else:
                # send cmd and params(username, password) to server
                self.send_cmd(cmd.encode(), params)
                # get response from server
                self.init_panel_destroy()

        else:
            self.try_again_label = Label(newWindow, text="Username or password are empty! Try again.")
            self.try_again_label.pack()
class Cli:
    def __init__(self):
        # open socket with the server
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.assigned_client_details = {}  # Create the dictionary globally


        self.root = Tk()

        # sets the geometry of main
        # root window
        self.root.geometry("300x300")
        self.root.title("Home Page")
        self.init_panel_create()


    def init_panel_create(self):
        self.label_welcome = Label(self.root,
                                   text="Welcome to VidPal!")
        self.label_welcome.pack(pady=10)
        # Create a Button
        self.btn_reg = Button(self.root, text='Register', command=self.Register_Window)
        self.btn_reg.place(x=30, y=100)


        # Create a Button
        self.btn_assign = Button(self.root, text='Log In', command=self.Assign_Window)
        self.btn_assign.place(x=200, y=100)

    def init_panel_destroy(self):
        self.label_welcome.destroy()
        self.label_welcome = None

        self.btn_reg.destroy()
        self.btn_reg = None

        self.btn_assign.destroy()
        self.btn_assign = None


    def connect(self, ip, port):
        self.my_socket.connect((ip, port))

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
            #עובד רק נכון לכרגע, אני מניחה כרגע שהדבר היחיד שאני מקבלת בפיקל הוא המילון, אני לא שולחת את הפקודה אלא יוצרת אותה
            # אם בעתיד אשלח עוד דברים בפיקל אצטרך להבדיל ביניהם!!!
            print("got the dict!!!!")
            cmd = "ASSIGNED_CLIENTS"
            #load pickle and not decode to get msg!!
            received_dict = pickle.loads(message)
            return True, cmd, received_dict
            #msg = received_dict
        else:
            msg = message.decode()
        message_parts = msg.split(Pro.PARAMETERS_DELIMITER) # message: cmd + len(params) + params
        print("0:" + message_parts[0] + "1:" + message_parts[1] )
        if message_parts[1] == '0':
            print("False!! no params, only cmd")
            return False, message_parts[0], None # return only cmd
        else:
            return True, message_parts[0], message_parts[2:] # return cmd, params

    def handle_response_Register(self, response):
        if response == Pro.cmds[Pro.REGISTER_NACK]:
            print("Maybe user already exist!!! try different username")
            return False
        elif response == Pro.cmds[Pro.REGISTER_ACK]:
            print("Registration succeedded")
            return True
        elif response == Pro.cmds[Pro.ASSIGN_NACK]:
            # they need to enter username and password again
            print("you need to enter password again")
            return False
            pass
        elif response == Pro.cmds[Pro.ASSIGN_ACK]:
            # add user to dift of assigned
            # create a token
            pass

    def handle_response_assign(self, response):
        if response == "ASSIGN_NACK":
            # they need to enter username and password again
            print("you need to enter password again")
            return False
        elif response == "ASSIGN_ACK":
            return True

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
            #self.handle_server_response(cmd, None)
            #if cmd == 'EXIT':
            #    return False
        #else:
            #print("Not a valid command, or missing parameters\n")

        return True


    #tkintern:

    def main_loop(self):
        self.root.mainloop()

    def Register_Window(self):

        cmd = "REGISTER"
        # Toplevel object which will
        # be treated as a new window
        newWindow = Toplevel(self.root)

        # sets the title of the
        # Toplevel widget
        newWindow.title("Register")

        # sets the geometry of toplevel
        newWindow.geometry("450x300")

        # the label for user_name
        self.user_name = Label(newWindow,text="Username")
        self.user_name.place(x=40,y=60)

        # the label for user_password
        self.user_password = Label(newWindow,text="Password")
        self.user_password.place(x=40, y=100)

        self.user_name_input_area = Entry(newWindow,width=30)
        self.user_name_input_area.place(x=110, y=60)

        self.user_password_entry_area = Entry(newWindow, width=30)
        self.user_password_entry_area.place(x=110, y=100)

        self.submit_button = Button(newWindow, text="Submit", command=lambda: self.submit_register(newWindow))
        self.submit_button.place(x=40, y=130)



    def submit_register(self, newWindow):

        # hasattr is a python function that checks if a value exists
        if hasattr(self, 'try_again_label'):
            self.try_again_label.destroy()

        if hasattr(self, 'try_again_label1'):
            self.try_again_label.destroy()

        if hasattr(self, 'already_registered_try_again'):
            self.already_registered_try_again.destroy()

        # Create a label indicating successful registration
        cmd = "REGISTER"
        username = self.user_name_input_area.get()
        password = self.user_password_entry_area.get()

        # Check if username and password are not empty
        if username.strip() and password.strip():
            print("the params:", username, password)

            params = [username.encode(), password.encode()]
            if not Pro.check_cmd_and_params(cmd, params):
                #Register_not_succeeded!!
                self.try_again_label1 = Label(newWindow, text="Couldn't Register! Try Again.")
                self.try_again_label1.pack()

                #self.Register_not_succeeded(newWindow)

            else:
                # send cmd and params(username, password) to server
                self.send_cmd(cmd.encode(), params)
                # get response from server
                res_response, msg_response = self.get_response()
                if res_response:
                    res_split_msg, cmd_response, params_response = self.split_message(msg_response)
                    if not res_split_msg:
                        # res_response = False: only got cmd (like in REGISTER N/ACK, ASSIGN N/ACK)
                        if (cmd_response == "REGISTER_NACK") or (cmd_response == "REGISTER_ACK"):
                            print("cmd is register")
                            response = self.handle_response_Register(cmd_response)

                            if not response:  # if false = REGISTER_NACK
                                # checking if the lable already exists
                                if not hasattr(self, 'already_registered_try_again'):
                                    self.already_registered_try_again = Label(newWindow, text="User Already Registered! Try To Log Inq Use Differente Username")
                                    self.already_registered_try_again.pack()

                                print("couldn't register (client already registered)")  # couldn't register/ client exists
                                print("continue to assign")
                                # client already exists! we need to continue to assign too
                                pass
                            else:
                                self.Register_succeeded(newWindow, self.submit_register)
                                print("you registered successfully")

                                pass

        else:
                self.try_again_label = Label(newWindow, text="Username or password are empty! Try again.")
                self.try_again_label.pack()

    def Register_succeeded(self, newWindow, submit_register):
        # Destroy the widgets in the registration window
        self.user_name.destroy()
        self.user_password.destroy()
        self.submit_button.destroy()
        self.user_name_input_area.destroy()
        self.user_password_entry_area.destroy()

        # Create a label indicating successful registration
        Label(newWindow, text="Registration succeeded").pack()

        # then continue: ask to Log In(assign)
        self.assigned_obj = AssignPanel(self.root, self.my_socket)
        self.Log_In_Register_Window = Button(newWindow, text="Log In",command=self.assigned_obj.init_panel_create)
        self.Log_In_Register_Window.place(x=40, y=130)

        # Create a button to close the window
        Button(newWindow, text="Close", command=newWindow.destroy).pack()

    def Register_not_succeeded(self, newWindow):
        # Destroy the widgets in the registration window
        self.user_name.destroy()
        self.user_password.destroy()
        self.submit_button.destroy()
        self.user_name_input_area.destroy()
        self.user_password_entry_area.destroy()

        # Create a label indicating successful registration
        Label(newWindow, text="Couldn't register, Try Again!").pack()

        # Create a button to close the window
        Button(newWindow, text="Close", command=newWindow.destroy).pack()

    def Assign_Window(self):
        # Toplevel object which will
        # be treated as a new window
        newWindow = Toplevel(self.root)

        # sets the title of the
        # Toplevel widget
        newWindow.title("Log In")

        # sets the geometry of toplevel
        newWindow.geometry("450x300")

        # the label for user_name
        self.user_name = Label(newWindow, text="Username")
        self.user_name.place(x=40, y=60)

        # the label for user_password
        self.user_password = Label(newWindow, text="Password")
        self.user_password.place(x=40, y=100)

        self.user_name_input_area = Entry(newWindow, width=30)
        self.user_name_input_area.place(x=110, y=60)

        self.user_password_entry_area = Entry(newWindow, width=30)
        self.user_password_entry_area.place(x=110, y=100)

        self.submit_button = Button(newWindow, text="Submit", command=lambda: self.submit_assign(newWindow))
        self.submit_button.place(x=40, y=130)

    def submit_assign(self, newWindow):

        # hasattr is a python function that checks if a value exists
        #if hasattr(self, 'try_again_label'):
        #    self.try_again_label.destroy()

        #if hasattr(self, 'try_again_label1'):
        #    self.try_again_label.destroy()

        cmd = "ASSIGN"
        username = self.user_name_input_area.get()
        password = self.user_password_entry_area.get()

        # Check if username and password are not empty
        if username.strip() and password.strip():
            print("the params:", username, password)

            params = [username.encode(), password.encode()]
            if not Pro.check_cmd_and_params(cmd, params):
                if not hasattr(self, 'try_again_label') or not self.try_again_label1:
                    # Assign not succeeded!!
                    self.try_again_label1 = Label(newWindow, text="Couldn't Log In! Try Again.")
                    self.try_again_label1.pack()

            else:
                # send cmd and params(username, password) to server
                self.send_cmd(cmd.encode(), params)
                # get response from server
                res_response, msg_response = self.get_response()
                if res_response:
                    res_split_msg, cmd_response, params_response = self.split_message(msg_response)
                    if not res_split_msg:
                        # res_response = False: only got cmd (like in REGISTER N/ACK, ASSIGN N/ACK)
                        if (cmd_response == "ASSIGN_NACK") or (cmd_response == "ASSIGN_ACK"):
                            print("cmd is assign")
                            response = self.handle_response_assign(cmd_response)

                            if response:  # if true = ASSIGN_ACK
                                print("user is assigned")
                                # user is assigned!! dict of assigned clients in is server!
                                self.AssignedPanel(newWindow)
                                pass

                            else:  # ASSIGN_NACK- Can't Log In! maybe user doesn't exists yet(isn't registered yet)
                                # checking if the lable already exists
                                if not hasattr(self, 'user_doesnt_exists_try_again')or not self.user_doesnt_exists_try_again:
                                    self.user_doesnt_exists_try_again = Label(newWindow, text="User doesnt exists! Try to Register Again")
                                    self.user_doesnt_exists_try_again.pack()

                                    # checking if the button already exists
                                    # register again button
                                    if not hasattr(self, 'user_doesnt_exists_try_again'):
                                        self.register_again = Button(newWindow, text="Submit",
                                                                    command=lambda: [newWindow.destroy(), self.Register_Window(newWindow)])
                                        self.register_again.place(x=40, y=130)


                                print(
                                    "couldn't register (client already registered)")  # couldn't register/ client exists
                                print("continue to assign")
                                # client already exists! we need to continue to assign too
        else:
            self.try_again_label = Label(newWindow, text="Username or password are empty! Try again.")
            self.try_again_label.pack()

    def AssignedPanel(self, newWindow):

        # when assigned- moving "into the system':
        # now you can look at contacts list and call whoever you want

        # Destroy the widgets in the log in window
        newWindow.destroy()
        self.btn_reg.destroy()
        self.btn_assign.destroy()
        self.label_welcome.destroy()

        self.root.title("Call (you are Logged In!)")

        # Create a Button
        self.btn_call = Button(self.root, text='Call', command=self.call_who_Window(newWindow))
        self.btn_call.place(x=120, y=100)

        # Create a Button
        self.btn_contact = Button(self.root, text='Contact List', command=self.Contact_List_window)
        self.btn_contact.place(x=120, y=130)

        # Create a Button
        #self.btn_reg = Button(self.root, text='Contact List', command=self.Contact_Window)
        # self.btn_reg.pack(side=LEFT)
        #self.btn_reg.place(x=30, y=100)

        # Create a button to close the window
        #Button(newWindow, text="Close", command=newWindow.destroy).pack()

    def Assign_not_succeeded(self, newWindow):
        # Destroy the widgets in the log in window
        self.user_name.destroy()
        self.user_password.destroy()
        self.submit_button.destroy()
        self.user_name_input_area.destroy()
        self.user_password_entry_area.destroy()

        # Create a label indicating successful registration
        Label(newWindow, text="Couldn't Log In, Try Again!").pack()

        # Create a button to close the window
        Button(newWindow, text="Close", command=newWindow.destroy).pack()

    def Contact_List_window(self):
        newWindow1 = Toplevel(self.root)
        # sets the title of the
        # Toplevel widget
        newWindow1.title("New Window")

        # sets the geometry of toplevel
        newWindow1.geometry("450x300")

        # the label for user_name
        self.user_name = Label(newWindow1, text="Your Contacts Are:")
        self.user_name.place(x=180, y=60)

    def call_who_Window(self, newWindow):

        # hasattr is a python function that checks if a value exists
        if hasattr(self, 'try_again_label1'):
            self.try_again_label1.destroy()

        if hasattr(self, 'try_again_label2'):
            self.try_again_label2.destroy()

        cmd = "CALL"
        newWindow1 = Toplevel(self.root)
        # sets the title of the
        # Toplevel widget
        newWindow1.title("Call")

        # sets the geometry of toplevel
        newWindow1.geometry("450x300")

        self.call_who = Label(newWindow1, text="Who Do You Want To Call To?")
        self.call_who.place(x=180, y=60)

        self.enter_username = Label(newWindow1, text="Enter Username:")
        self.enter_username.place(x=40, y=100)

        self.username_input_area = Entry(newWindow1, width=30)
        self.username_input_area.place(x=110, y=100)

        username = self.username_input_area.get()
        # Check if username is not empty
        if username.strip():
            print("he wants to call:", username)
            target_username = self.username_input_area.get()

            params = [target_username.encode()]
            if not Pro.check_cmd_and_params(cmd, params):
                # in this phase only REGISTER or ASSIGN is required with [username, password] as params
                print("Invalid command! Try again!")

                # user isnt registered!!!
                self.try_again_label1 = Label(newWindow1, text="Invalid command! Try again!")
                self.try_again_label1.pack()


            self.send_cmd(cmd.encode(), params)

            res_response, msg_response = self.get_response()
            if res_response:
                res_split_msg, cmd_response, params_response = self.split_message(msg_response)
                if res_split_msg:
                    # res_response = True: got cmd and params (meaning cmd = ASSIGNED_CLIENTS)
                    if (cmd_response == "TARGET_NACK") or (cmd_response == "TARGET_ACK"):
                        print("cmd is call(call target client)")
                        client_username = params_response[0]
                        response = self.handle_response_call_target(cmd_response)
                        if response:  # if true = ASSIGN_ACK
                            print("we can call target! he is assigned")

                            # get target details

                            # getting target details from server dict client_sockets_details
                            # getting ip and port according to username

                            cmd = "ASK_TARGET_DETAILS"
                            tof = Pro.check_cmd(cmd)
                            if tof:
                                # sending to server
                                cmd_send = Pro.create_msg(cmd.encode(), [client_username.encode()])
                                self.my_socket.send(cmd_send)

                            # get response from server
                            # should i wait for response from server??? not assume i get it
                            res_response, msg_response = self.get_response()
                            if res_response:
                                res_split_msg1, cmd_response1, params_response1 = self.split_message(msg_response)
                                if res_split_msg1:
                                    # res_response = True: got cmd and params
                                    if (cmd_response1 == "SEND_TARGET_DETAILS"):
                                        print("cmd is SEND_TARGET_DETAILS")
                                        client_socket_details = params_response1
                                        print("got the client details params!!!:", client_socket_details)
                            pass

                        else:  # REGISTER_NACK- Maybe user already exist!!! try different username
                            print("couldn't call target!")
                            print("call another person: (from contacts)")






        else:
            self.try_again_label2 = Label(newWindow1, text="It's Empty! Write again")
            self.try_again_label2.pack()




def Main():
    myclient = Cli()
    myclient.connect("127.0.0.1", Pro.PORT)
    myclient.main_loop()


if __name__ == "__main__":
    Main()
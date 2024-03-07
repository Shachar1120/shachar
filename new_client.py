import socket
import pickle
#import cv2
import threading

#import negotitate
from new_protocol import Pro
from new_server import Ser


class Cli:
    SAVED_PHOTO_LOCATION = r"c:\users\galis\pictures\screenshot.jpg" # The path + filename where the copy of the screenshot at the client should be saved

    def __init__(self):
        # open socket with the server
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.assigned_client_details = {}  # Create the dictionary globally

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
            # add user to dift of assigned
            # create a token
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


    def check_client_assigned(self, params):
        # check if client is assigned = in assigned dict
        # send username to server
        sending_username = Pro.create_msg(cmd.encode(), [])
        self.my_socket.send(sending_cmd)
        # server checks if username in dict
        if params[0].decode() in Ser.assigned_clients.keys():
            return True
        else:
            return False



    def assigned_mode(self, params):

        print("moved to assigned mode")
        # client wants to start a call
        # print all of assigned clients(print assigned dict)

        # ask server for the assigned_clients dict
        cmd_assigned_clients = "ASSIGNED_CLIENTS"
        # send request for contact list(all of assigned clients) to server
        ask_assigned_clients = Pro.create_msg(cmd_assigned_clients.encode(), [])
        self.my_socket.send(ask_assigned_clients)

        # receiving assigned clients dictionary
        #res, assigned_clients_dict = Pro.get_msg(self.my_socket)
        #if res:
            #print("Received assigned clients dictionary successfully")
            #assigned_clients = pickle.loads(assigned_clients_dict)
            #print("the Assigned clients dict is:", assigned_clients)
        #else:
            #print("Error receiving assigned clients dictionary")


        # check if client is assigned = in assigned dict
        #if self.check_client_assigned(params):
            #get client details: username, (ip, port)
        #    if params[0] in Ser.client_sockets_details.keys(): #if username is in dict
        #        ip, port = Ser.client_sockets_details[params[0]] #(ip, port)
        #        print("this is the ip and port:", ip, port)
         #       print("here!!!!!!", ip, port)



        # create a call token
        # enter cmd to start streaming
        #get_cmd = input("Please enter command:\n").upper()
        #self.handle_cmd(get_cmd)
        # get_cmd = input("Please enter command:\n").upper()
        # res = self.handle_cmd(get_cmd)
        #return True
        #pass


def main():
    myclient = Cli()
    myclient.connect("127.0.0.1", Pro.PORT)

    while True:
        print(f"options: \n\tregister\n\tassign\n\tcontacts\n> ", end=" ")
        cmd = input()
        cmd = cmd.upper()

        if Pro.check_register_or_assign(cmd):
            print("Enter username:")
            username = input()
            print("Enter password:")
            password = input()
            params = [username.encode(), password.encode()]
            if not Pro.check_cmd_and_params(cmd, params):
                # in this phase only REGISTER or ASSIGN is required with [username, password] as params
                print("Invalid command! Try again!")
                continue
        elif Pro.check_contacts(cmd):
            if not Pro.check_cmd_and_params(cmd):
                # in this phase only REGISTER or ASSIGN is required with [username, password] as params
                print("Invalid command! Try again!")
                continue
        else:
            # in this phase only REGISTER or ASSIGN is required
            print("Invalid command! Try again!")
            continue

        myclient.send_cmd(cmd.encode(), params)

        res, cmd_response = myclient.get_response()  # res, params = REGISTER_NACK/REGISTER_ACK,
        cmd_response = cmd_response.decode()
        #message_parts = cmd_response.split(Pro.PARAMETERS_DELIMITER)
        #cmd_part = message_parts[0]
        #params = message_parts[1:]
        print(params)
        if res:
            if (cmd_response == "REGISTER_NACK") or (cmd_response == "REGISTER_ACK"):
                print("cmd is register")
                response = myclient.handle_response_Register(cmd_response)
                if not response: # if false = REGISTER_NACK
                    print("couldn't register (client already registered)") # couldn't register/ client exists
                    print("continue to assign")
                    #client already exists! we need to continue to assign too
                    pass
                else:
                    print("you registered successfully")
                    # then continue: ask to assign
                    pass
            else:
                print("cmd isnt register")

            if (cmd_response == "ASSIGN_NACK") or (cmd_response == "ASSIGN_ACK"):
                print("cmd is assign")
                response = myclient.handle_response_assign(cmd_response)
                if response: # if true = ASSIGN_ACK
                    print("user is assigned")
                    # user is assigned!!
                    # dict of assigned clients in is server!

                    pass
                else: # REGISTER_NACK- Maybe user already exist!!! try different username
                    print("couldn't register")
                    print("password or username are incorrect!! write again:")
                    pass

            #if(cmd_response.decode() == "ASSIGNED_CLIENTS"):
               # print("got the message!!!")
                #pickle loads!!
                #print("ok!!")

        else:
            break


if __name__ == '__main__':
    main()

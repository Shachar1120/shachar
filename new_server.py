import pickle
import socket
import threading
import select

from new_protocol import Pro
#from camera import Cam

import glob
import os
import shutil
import subprocess
#import cv2
import time

class Ser:
    IP = "0.0.0.0"

    def __init__(self, ip, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen()
        print("Server is up and running")

        self.client_sockets = []

        #self.registered = False

        # {"username1": "password1", "username2": "password2",...}:
        self.client_details = {} # dict of all the registered clients(all of the clients in the system) Username: (password, port)
        self.assigned_clients = {} # dict of all usernames of assigned client(right now)
        self.client_sockets_details = {} #{"username1" : "(ip, port)" # i have to check there isnt a username already!!!

    def accept(self):
        (client_socket, client_address) = self.server_socket.accept()
        self.client_sockets.append(client_socket)
        print("Client connected")

    def client_disconnected(self, client_socket):
        self.client_sockets.remove(client_socket)
        print("Client disconnected")

    def handle_registration(self, params: [], client_socket) -> int:

        # get client username and socket details
        # the port of the client server(my_port in client)!!
        call_accept_port = int(params[2])  # client sends it in str, we need to change to int
        print("the Port:", call_accept_port)

        if params[0] in self.client_details.keys(): #if username exists in dictionary
            return Pro.cmds[Pro.REGISTER_NACK] # already registered

        # else: user is not registered yet
        # registering = adding client to dictionary
        #Username: (password, port)
        self.client_details[params[0]] = (params[1], call_accept_port) #add client
        print("client details dict:", self.client_details)



        return Pro.cmds[Pro.REGISTER_ACK]



    def handle_assigned(self, params: [], client_socket) -> int:

        username_value = params[0]

        if self.check_password(params):
            print("Correct Password!!")

            # add to dict of assigned clients
            #if client isnt assigned yet
            if self.check_client_assigned(username_value): # if client already in dictinary
                print("this user is already assigned on another device!")
                return Pro.cmds[Pro.ASSIGN_NACK]  # username not! acknowledged
            else:
                # else: user is not assigned yet
                # registering = adding client to dictionary
                # Username: (password, port)
                client_server_details = self.client_details[username_value]  # (password, port)
                self.assigned_clients[username_value] = client_server_details  # add client
                print("assigned_clients dict:", self.assigned_clients)
                return Pro.cmds[Pro.ASSIGN_ACK]  # username acknowledged



    def check_password(self, params: []):
        username_value = params[0]
        user_details_value = params[1] #(password, port)
        username_in_dict = self.client_details[username_value] # username: (password, port)

        # check username is even registered
        if username_value in self.client_details.keys():
            #check if password fit
            # if (password in dictionary) == (password in params)
            if username_in_dict[0] == user_details_value[0]: #if password of username in dict match password from params
                return True
        return False

    def check_client_request(self, data):
        # Use protocol.check_cmd first
        tof = Pro.check_cmd(data)
        if tof:
            cmd = data
            if cmd == 'START_STREAMING' or cmd == 'STOP_STREAMING':
                return True, cmd
        else:
            return False, cmd

    def handle_client_request(self, command):
        if command == 'START_STREAMING':
            self.camera(command)
        elif command == 'STOP_STREAMING':
            pass


    def split_msg(self, message):
        message = message.decode()
        message_parts = message.split(Pro.PARAMETERS_DELIMITER)  # message: cmd + len(params) + params
        if message_parts[1] == '0': # len(params) == 0
            # no params, only cmd
            return False, message_parts[0], None  #return cmd only
        else:
            return True, message_parts[0], message_parts[2:]  #  return cmd, params


    def handle_call(self, username_param):
        res = self.check_client_assigned(username_param)
        if res:
            print("you can call client, he is assigned")
            # target ACK
            return Pro.cmds[Pro.TARGET_ACK]  # username(=target) acknowledged
        else:
            print("client isn't assigned! you cant call him")
            # target NACK
            return Pro.cmds[Pro.TARGET_NACK]  # username not acknowledged!

    def check_client_assigned(self, username):
        if username in self.assigned_clients.keys():
            return True
        return False

def main():
    # open socket with client
    myserver = Ser(Ser.IP, Pro.PORT)


    # handle requests until user asks to exit
    while True:
        rlist, _, _ = select.select([myserver.server_socket] + myserver.client_sockets, [], [])

        # for i in range(len(rlist)):
            # current_socket = rlist[i]
        for current_socket in rlist:
            if current_socket == myserver.server_socket:
                # server accept
               myserver.accept()

            else:
                # client handling: current_socket is one of the self.client_sockets
                res, message = Pro.get_msg(current_socket)
                if not res:
                    myserver.client_disconnected()

                # check if you have cmd + params or only cmd
                res_split, cmd_res, params_res = myserver.split_msg(message)
                if res_split:
                    #res_response = True: got both cmd and params (like in REGISTER , ASSIGN)

                    # if REGISTER:
                    if cmd_res == Pro.cmds[Pro.REGISTER]:
                        res = myserver.handle_registration(params_res, current_socket) # return REGISTER_NACK or REGISTER_ACK
                        # send response to the client
                        message = Pro.create_msg(res.encode(), [])
                        current_socket.send(message)

                    # if ASSIGNED:
                    elif cmd_res == Pro.cmds[Pro.ASSIGN]:
                        print("cmd is assign!!")
                        res = myserver.handle_assigned(params_res, current_socket)
                        # send response to the client
                        message = Pro.create_msg(res.encode(), [])
                        current_socket.send(message)

                    elif cmd_res == Pro.cmds[Pro.CALL]:
                        print("cmd is call!!")
                        res = myserver.handle_call(params_res)
                        # send response to the client
                        client_username = params_res[0]
                        message = Pro.create_msg(res.encode(), [client_username.encode()])
                        current_socket.send(message)

                    elif cmd_res == Pro.cmds[Pro.ASK_TARGET_DETAILS]:
                        print("cmd is ASK_TARGET_DETAILS!!")
                        client_username = params_res[0]
                        # get client details(ip and port) from client_sockets_details dict
                        print("client_sockets_details!!:", myserver.client_sockets_details[client_username])
                        client_ip, client_port = myserver.client_sockets_details[client_username] # tuple (ip, port)
                        client_port = str(client_port)

                        # send details to the client
                        cmd_to_send = Pro.cmds[Pro.SEND_TARGET_DETAILS]
                        message = Pro.create_msg(cmd_to_send.encode(), [client_ip.encode(), client_port.encode()])
                        current_socket.send(message)


                
                else:
                    #res_response = False: only got cmd (cmd = CONTACTS)

                    # client asks for assigned clients dict
                    if cmd_res == Pro.cmds[Pro.CONTACTS]:
                        print("got the message contacts!!!!!")

                        # send response to the client
                        cmd_to_send = Pro.cmds[Pro.ASSIGNED_CLIENTS]
                        print("this is the dict!!!:", myserver.assigned_clients)
                        send_dict = pickle.dumps(myserver.assigned_clients)
                        message = Pro.create_msg(send_dict, [])
                        current_socket.send(message)




    # close sockets
    print("Closing connection")
    myserver.close()

if __name__ == '__main__':
    main()

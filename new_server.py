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
        self.client_details = {} # dict of all the registered clients(all of the clients in the system)
        self.assigned_clients = {} # dict of all assigned client(as in right now)
        self.client_sockets_details = {} #{"username1" : "(ip, port)" # i have to check there isnt a username already!!!

    def accept(self):
        (client_socket, client_address) = self.server_socket.accept()
        self.client_sockets.append(client_socket)
        print("Client connected")

    def client_disconnected(self, client_socket):
        self.client_sockets.remove(client_socket)
        print("Client disconnected")

    def handle_registration(self, params: [], client_socket) -> int:
        if params[0] in self.client_details.keys(): #if username exists in dictionary
            return Pro.cmds[Pro.REGISTER_NACK] # already registered

        # else: user is not registered yet
        # registering:
        self.client_details[params[0]] = params[1] #add client

        # add client username and socket details
        self.client_sockets_dict_details(params, client_socket)

        return Pro.cmds[Pro.REGISTER_ACK]

    def client_sockets_dict_details(self, params: [], client_socket):
        # get client socket details: ip and port
        ip = client_socket.getpeername()[0]
        port = client_socket.getpeername()[1]
        print(f"Username: {params[0]}, IP: {ip}, Port: {port}")
        # add client username and socket details
        self.client_sockets_details[params[0]] = (ip, port) # add client
        #print("this is the client_sockets_details dict!!!!")
        print(self.client_sockets_details)

    def handle_assigned(self, params: []) -> int:
        if self.check_password(params):
            print("Correct Password!!")
            return Pro.cmds[Pro.ASSIGN_ACK]  # username acknowledged
        else:
            print("Incorrect password!!")
            return Pro.cmds[Pro.ASSIGN_NACK]  # username not! acknowledged

        # add user to dict of assigned
        self.assigned_clients[params[0]] = params[1] #add client





    def check_password(self, params: []):
        # check username already registered
        if params[0] in self.client_details.keys():
            #check if password fit
            password_value = self.client_details[params[0]]
            if password_value == params[1]: #if password of username in dict match password from params
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

    def assigned_mode_server(self, cmd):
        print("server is in assigned mode!!")
        # send the assigned_clients dict to client to print contact list
        #message = Pro.create_msg(b"ASSIGNED_CLIENTS", [pickle.dumps(self.assigned_clients)])
        message = Pro.create_msg(b"ASSIGNED_CLIENTS", [pickle.dumps(self.assigned_clients)])
        print("here!!")
        self.client_sockets.send(message.encode())
        #reciving a command

        #cmd_params = cmd.decode().split(" ")
        #valid_cmd, command = self.check_client_request(cmd_params[0]) #cmd_params[0] = the cmd (ASSIGN for example)
        # prepare a response using "handle_client_request"
        #response = self.handle_client_request(command)


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

                message = message.decode()
                message_parts = message.split(Pro.PARAMETERS_DELIMITER)
                cmd = message_parts[0]
                params = message_parts[1:]
                # if REGISTER:
                if cmd == Pro.cmds[Pro.REGISTER]:
                    res = myserver.handle_registration(params, current_socket) # return REGISTER_NACK or REGISTER_ACK
                    # send response to the client
                    message = Pro.create_msg(res.encode(), [])
                    current_socket.send(message)

                # if ASSIGNED:
                elif cmd == Pro.cmds[Pro.ASSIGN]:
                    print("cmd is assign!!")
                    res = myserver.handle_assigned(params)
                    # send response to the client
                    message = Pro.create_msg(res.encode(), [])
                    current_socket.send(message)

                    #valid_protocol, cmd = Pro.get_msg(current_socket)  # מקבלת פקודה מהלקוח
                    #print(f"received: {cmd} and validation turn out {valid_protocol}")
                    #if valid_protocol:
                    while myserver.assigned_mode_server(cmd):
                            continue

    # close sockets
    print("Closing connection")
    myserver.close()

if __name__ == '__main__':
    main()

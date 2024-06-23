import pickle
import socket
import threading
import select
import mysql.connector
import hashlib

from new_protocol import Pro
from DataBase import DataBase
# from camera import Cam

import glob
import os
import shutil
import subprocess
# import cv2
import time


class Ser:
    IP = "0.0.0.0"

    def __init__(self, ip, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen()
        print("Server is up and running")

        self.client_sockets = []

        self.database_obj = DataBase("mydatabase")

        self.assigned_clients = {}  # dict of all usernames of assigned client(right now)


    def accept(self):
        (client_socket, client_address) = self.server_socket.accept()
        self.client_sockets.append(client_socket)
        print("Client connected")

    def client_disconnected(self, client_socket):
        self.client_sockets.remove(client_socket)
        print("Client disconnected")

    def encrypte_password(self, password):
        password = hashlib.md5(password.encode()).hexdigest()
        return password

    def handle_registration(self, params: [], client_socket) -> int:

        # get client username and socket details
        # the port of the client server(my_port in client)!!

        username = params[0]
        password = params[1]
        call_accept_port = int(params[2])  # client sends it in str, we need to change to int
        print("the Port:", call_accept_port)

        encrypte_password = self.encrypte_password(password)
        # בדוק אם שם המשתמש פנוי
        if self.database_obj.is_username_in_database(username):
            # צור חשבון חדש
            self.database_obj.create_new_account(username, encrypte_password, call_accept_port)
            return Pro.cmds[Pro.REGISTER_ACK]
        else:
            return Pro.cmds[Pro.REGISTER_NACK]  # already registered



    def handle_assigned(self, params: [], client_socket) -> int:

        #בהתחברות אנחנו עדיין משתמשים במילון
        # רק בהרשמה אנחנו משתמשים בדאטאבייס!!!
        username_value = params[0]


        if self.check_password(params): # checks if username exits in database(is registered) and if password is correct
            print("Correct Password!!")

            # add to dict of assigned clients
            # if client isnt assigned yet
            if self.check_client_assigned(username_value):  # if client already in dictinary
                print("this user is already assigned on another device!")
                return Pro.cmds[Pro.ASSIGN_NACK]  # username not! acknowledged
            else:
                # else: user is not assigned yet
                # registering = adding client to dictionary
                # Username: (password, port)
                username_value = params[0]
                password, port = self.database_obj.find_username_info_database(username_value) #takes it from database

                self.assigned_clients[username_value] = port #(password(???), port) # add client
                print("assigned_clients dict:", self.assigned_clients)
                return Pro.cmds[Pro.ASSIGN_ACK]  # username acknowledged

        else:
            print("check password failed!!!")


    def check_password(self, params: []):
        username_input = params[0]
        user_details_value = params[1]  # password
        user_details_value = self.encrypte_password(user_details_value)

        # check username is even registered
        if not self.database_obj.is_username_in_database(username_input): # if =False that means the username is registered
            password_in_Database, port_in_Database = self.database_obj.find_username_info_database(username_input)
            # check if password fit
            # if (password in dictionary) == (password in params)
            if password_in_Database == user_details_value:  # if password of username in dict match password from params
                return True
        return False



    def split_cmd_params_msg(self, message):
        message_parts = message.split(Pro.PARAMETERS_DELIMITER)  # message: cmd + len(params) + params
        opcode = message_parts[0]
        nof_params = int(message_parts[1]) # number of params
        params = message_parts[2:]
        return opcode, nof_params, params



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
                message = message.decode()
                if not res:
                    myserver.client_disconnected()

                # check if you have cmd + params or only cmd
                cmd_res, nof_res, params_res = myserver.split_cmd_params_msg(message)

                # if REGISTER:
                if cmd_res == Pro.cmds[Pro.REGISTER]:
                    res = myserver.handle_registration(params_res,
                                                       current_socket)  # return REGISTER_NACK or REGISTER_ACK
                    # send response to the client
                    message = Pro.create_msg(res.encode(), [])
                    current_socket.send(message)

                    # if ASSIGNED:
                elif cmd_res == Pro.cmds[Pro.ASSIGN]:
                    print("cmd is assign!!")
                    res = myserver.handle_assigned(params_res, current_socket)
                    print("res!!!", res)
                    # send response to the client
                    message = Pro.create_msg(res.encode(), [])
                    current_socket.send(message)


                # client asks for assigned clients dict
                elif cmd_res == Pro.cmds[Pro.CONTACTS]:
                    print("got the message contacts!!!!!")

                    # send response to the client
                    cmd_to_send = Pro.cmds[Pro.ASSIGNED_CLIENTS]
                    print("this is the dict!!!:", myserver.assigned_clients)
                    send_dict = pickle.dumps(myserver.assigned_clients)
                    print("send_dict!!", send_dict)
                    message = Pro.create_msg(cmd_to_send.encode(), [send_dict])
                    current_socket.send(message)



    # close sockets
    print("Closing connection")
    myserver.close()


if __name__ == '__main__':
    main()
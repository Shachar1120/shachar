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
import cv2
import time

class Ser:
    IP = "0.0.0.0"

    def __init__(self, ip, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen()
        print("Server is up and running")

        self.client_sockets = []

        self.registered = False
        # {"username1": "password1", "username2": "password2",...}
        self.client_details = {}  # Create the dictionary globally

    def accept(self):
        (client_socket, client_address) = self.server_socket.accept()
        self.client_sockets.append(client_socket)
        print("Client connected")

    def client_disconnected(self, client_socket):
        self.client_sockets.remove(client_socket)
        print("Client disconnected")

    def handle_registration(self, params: []) -> int:
        if params[0] in self.client_details.keys():
            return Pro.cmds[Pro.REGISTER_NACK] # already registered

        # registering:
        self.client_details[params[0]] = params[1]
        return Pro.cmds[Pro.REGISTER_ACK]

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

                # cmd = message_parts[0], params = message_parts[1:]
                message_parts = message.split(Pro.PARAMETERS_DELIMITER)
                cmd = message_parts[0], params = message_parts[1:]
                # if REGISTER:
                if cmd == Pro.cmds[Pro.REGISTER]:
                    res = myserver.handle_registration(params)
                    # send response to the client
                    message = Pro.create_msg(res, [])
                    current_socket.send(message)

                # if ASSIGNED:
                elif cmd == Pro.cmds[Pro.ASSIGN]:
                    pass
                else:
                    pass

    # close sockets
    print("Closing connection")
    myserver.close()

if __name__ == '__main__':
    main()
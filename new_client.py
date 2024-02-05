import socket
import pickle
import cv2
import threading

import negotitate
from new_protocol import Pro


class Cli:
    SAVED_PHOTO_LOCATION = r"c:\users\galis\pictures\screenshot.jpg" # The path + filename where the copy of the screenshot at the client should be saved

    def __init__(self):
        # open socket with the server
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip, port):
        self.my_socket.connect((ip, port))

    def send_cmd(self, cmd: bytes, params:[]):
        msg_to_send = Pro.create_msg(cmd, params)
        self.my_socket.send(msg_to_send)

    def get_response(self):
        res, message = Pro.get_msg(self.my_socket)
        if not res:
            return False, None

        return True, message
    def handle_response(self, response):
        # cmd = message_parts[0], params = message_parts[1:]
        message_parts = response.split(Pro.PARAMETERS_DELIMITER)
        cmd = message_parts[0], params = message_parts[1:]
        if cmd == Pro.cmds[Pro.REGISTER_NACK]:
            print("Maybe user already exist!!! try different username")
            return False
        elif cmd == Pro.cmds[Pro.REGISTER_ACK]:
            print("Registration succeedded")
            return True
def main():
    myclient = Cli()
    myclient.connect("127.0.0.1", Pro.PORT)

    while True:
        print(f"options: \n\tregister\n\tassign\n> ", end=" ")
        cmd = input()
        cmd = cmd.upper()

        if not Pro.check_register_or_assign(cmd):
            # in this phase only REGISTER or ASSIGN is required
            print("Invalid command! Try again!")
            continue

        print("Enter username:")
        username = input()
        print("Enter password:")
        password = input()
        params = [username.encode(), password.encode()]
        if not Pro.check_cmd_and_params(cmd, params):
            # in this phase only REGISTER or ASSIGN is required with [username, password] as params
            print("Invalid command! Try again!")
            continue

        myclient.send_cmd(cmd.encode(), params)

        res, response = myclient.get_response()
        if res:
            myclient.handle_response(response)
        else:
            break


if __name__ == '__main__':
    main()

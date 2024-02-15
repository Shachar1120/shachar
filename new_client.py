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

        self.assigned_client_details = {}  # Create the dictionary globally

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
    def handle_response_Register(self, response):
        cmd = response
        if cmd == Pro.cmds[Pro.REGISTER_NACK]:
            print("Maybe user already exist!!! try different username")
            return False
        elif cmd == Pro.cmds[Pro.REGISTER_ACK]:
            print("Registration succeedded")
            return True
        elif cmd == Pro.cmds[Pro.ASSIGN_NACK]:
            # they need to enter username and password again
            print("you need to enter password again")
            return False
            pass
        elif cmd == Pro.cmds[Pro.ASSIGN_ACK]:
            # add user to dift of assigned
            # create a token
            pass

    def handle_response_Assign(self, response):
        cmd = response
        if cmd == Pro.cmds[Pro.ASSIGN_NACK]:
            # they need to enter username and password again
            print("you need to enter password again")
            return False
            pass
        elif cmd == Pro.cmds[Pro.ASSIGN_ACK]:
            # add user to dift of assigned
            # create a token
            pass

    def handle_cmd(self, cmd):
        tof, msg = Pro.check_cmd(cmd)
        if tof:
            # sending to server
            send_cmd = Pro.create_msg(cmd.encode())
            self.my_socket.send(send_cmd)

            # receiving from server
            #self.handle_server_response(cmd, None)
            #if cmd == 'EXIT':
            #    return False
        #else:
            #print("Not a valid command, or missing parameters\n")

        return True




def assigned_mode(params):
    # create a call token
    # enter cmd to start streaming
    # get_cmd = input("Please enter command:\n").upper()
    # res = self.handle_cmd(get_cmd)
    return True
    pass


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

        res, cmd_response = myclient.get_response() #res, params = REGISTER_NACK/REGISTER_ACK,
        if res:
            print("here!!!")
            if (cmd_response == Pro.cmds[Pro.REGISTER_NACK]) or (cmd_response == Pro.cmds[Pro.REGISTER_ACK]):
                response = myclient.handle_response_Register(cmd_response.decode())
                if response: # if true = REGISTER_ACK

                    pass
                else:
                    # couldn't register/ client exists
                    pass

            if (cmd_response == Pro.cmds[Pro.ASSIGN_NACK]) or (cmd_response == Pro.cmds[Pro.ASSIGN_ACK]):
                response = myclient.handle_response_Assign(cmd_response.decode())
                if response: # if true = ASSIGN_ACK
                    # user is assigned!!
                    # move to assigned mode:
                    while myclient.assigned_mode(params):
                        continue
                    #
                    pass
                else: # REGISTER_NACK- Maybe user already exist!!! try different username
                    pass

        else:
            break


if __name__ == '__main__':
    main()

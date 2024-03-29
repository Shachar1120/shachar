import socket
import pickle
import cv2
import threading

import negotitate
from protocol import Pro

BUFFER_SIZE = 4096


class Cli:
    SAVED_PHOTO_LOCATION = r"c:\users\galis\pictures\screenshot.jpg" # The path + filename where the copy of the screenshot at the client should be saved

    def __init__(self):
        # open socket with the server
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)




    def connect(self, ip, port):

        master_or_slave = input("Are you a Master or a Slave?").upper()

        if master_or_slave == "MASTER":
            connect_details = (ip, port, 1)  # client_details = (ip, port, master)
        elif master_or_slave == "SLAVE":
            connect_details = (ip, port, 2) #client_details = (ip, port, slave)
        else:
            print('error! write again master or slave')


        self.my_socket.connect((ip, port))


    #def call_another(self, connect_details):
        #if connect_details[2] == 1:  # is master of the call
        #    call_code = input("Please enter a call code").upper()
        #else if connect_details[2] == 2:  # is master of the slave

    def handle_server_response(self, cmd, connect_details):
        """
        Receive the response from the server and handle it, according to the request
        For example, DIR should result in printing the contents to the screen,
        Note- special attention should be given to SEND_PHOTO as it requires and extra receive
        """

        while True:
            isTrue, msg = Pro.get_msg(self.my_socket)
            if isTrue:
                # Display the frame
                self.receive_frame()
                print("heyyy")
            else:
                print("Error receiving frame from the server.")
                break

        # (10) treat SEND_PHOTO

    def assign(self, username, password):
        # send again to server to check password:
        details_again_msg = f"{Pro.CHECK}{Pro.PARAMETERS_DELIMITER}{username}{Pro.PARAMETERS_DELIMITER}{password}".encode()
        # sending to server
        packet = Pro.create_msg(details_again_msg)
        self.my_socket.send(packet)

        # receiving from server
        isTrue1, msg_again = Pro.get_msg(self.my_socket)

        check = msg_again.decode()
        if check == "True":
            return True
        else:
            return False

    def handle_cmd(self,cmd):
        # check if master or slave:
        tof, msg = Pro.check_cmd(cmd)
        if tof:
            # sending to server
            packet = Pro.create_msg(cmd.encode())
            self.my_socket.send(packet)

            # receiving from server
            self.handle_server_response(cmd, None)
            if cmd == 'EXIT':
                return False
        else:
            print("Not a valid command, or missing parameters\n")

        return True




    @property
    def donext(self):

        username = input("Please enter your name").upper()
        password = input("Please enter your password").upper()

        #message = f"{Pro.REGISTER}{Pro.PARAMETERS_DELIMITER}{username}{Pro.PARAMETERS_DELIMITER}{password}".encode()
        message = f"{username}{Pro.PARAMETERS_DELIMITER}{password}".encode()
        # sending to server
        packet = Pro.create_msg(message)
        self.my_socket.send(packet)

        # receiving from server
        isTrue, msg = Pro.get_msg(self.my_socket)

        register = msg.decode()
        if register == "True":
            #enter details again:
            username2 = input("Please enter your name again").upper()
            password2 = input("Please enter your password again").upper()

            if self.assign(username2, password2):
                print("your username and password are ok")

                get_cmd = input("Please enter command:\n").upper()
                self.handle_cmd(get_cmd)
            else:
                print("your password is incorrect")

            #get out of the loop
        if register == "False":
                print("you havent signed up yet")
                break

    def receive_frame(self):
        frame_data = b""

        while True:
            res, frame_data = Pro.get_msg(self.my_socket)
            if res:
                self.display_frame(frame_data)


        #img_encoded = pickle.loads(frame_data)
        #frame = cv2.imdecode(img_encoded, cv2.IMREAD_COLOR)
        #cv2.imshow('Server Stream', frame)
        #cv2.waitKey(1)


    def display_frame(self, frame_data):
        img_encoded = pickle.loads(frame_data)
        frame = cv2.imdecode(img_encoded, cv2.IMREAD_COLOR)
        cv2.imshow('Server Stream', frame)
        cv2.waitKey(1)




    def close(self):
        self.my_socket.close()


def print_usage():
    print(f"options: \n\tregister\n\tassign")
def main():
    #client_details = {"username": [], "password": []}  # dictionary

    myclient = Cli()
    myclient.connect("127.0.0.1", Pro.PORT)
    print('Welcome to remote computer application. Available commands are:\n')
    print('START_STREAMING\nSTOP_STREAMING\nEXIT')
    while myclient.donext:
        continue
    myclient.close()
    # (2)

    # print instructions


    # my_socket.send(protocol.create_msg(cmd).encode())


    # loop until user requested to exit


if __name__ == '__main__':
    main()

# note right of Server: Client connect to server
# Client1->Server: connect ServerSocket
# Server->Client1: ServerSocket accept
#
# note right of Client: Client sends start_streaming
# Client1->Server: start_streaming
# Server->Client1: ServerSocket accept
# Server->Client1: send_frame 1
# Server->Client1: send_frame 2
# Server->Client1: send_frame 3
#...
# Server->Client1: send_frame infinite...

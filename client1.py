import socket
import pickle
import cv2
import threading

from protocol import Pro

BUFFER_SIZE = 4096


class Cli:
    SAVED_PHOTO_LOCATION = r"c:\users\galis\pictures\screenshot.jpg" # The path + filename where the copy of the screenshot at the client should be saved

    def __init__(self):
        # open socket with the server
        self.registered = False
        self.client_details = {"username": [], "password": []} # Create the dictionary globally
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)




    def connect(self, ip, port):
        username = input("Please enter your name1").upper()
        password = input("Please enter your password1").upper()

        # Add the new user to the global dictionary
        self.client_details["username"].append(username)
        self.client_details["password"].append(password)


        master_or_slave = input("Are you a Master or a Slave?").upper()

        if master_or_slave == "MASTER":
            connect_details = (ip, port, 1)  # client_details = (ip, port, master)
        elif master_or_slave == "SLAVE":
            connect_details = (ip, port, 2) #client_details = (ip, port, slave)
        else:
            print('error! write again master or slave')


        self.my_socket.connect((ip, port))

    def check_password(self, username, password):
        # Check if the username exists in the dictionary
        #if username is self.client_details["username"]:
            # Get the index of the username
            index = self.client_details["username"].index(username) #למצוא את המיקום במילון

            # Check if the provided password matches the stored password for that username
            if self.client_details["password"][index].upper() == password:
                return True
            else:
                print("Incorrect password.")
                return False
        #else:
            #print("Username not found.")
            #return False

    def handle_server_response(self, cmd):
        """
        Receive the response from the server and handle it, according to the request
        For example, DIR should result in printing the contents to the screen,
        Note- special attention should be given to SEND_PHOTO as it requires and extra receive
        """
        while True:
            isTrue, msg = Pro.get_msg(self.my_socket)
            if isTrue:
                # Display the frame in a separate thread

                #receive_thread = threading.Thread(target=self.receive_frame)
                #receive_thread.start()
                # Display the frame
                self.receive_frame()
                print("heyyy")
            else:
                print("Error receiving frame from the server.")
                break



        # (10) treat SEND_PHOTO

    def donext(self):

        if self.registered == False: #still haven't registered

            username = input("Please enter your name2").upper()
            password = input("Please enter your password2").upper()

            print(self.client_details)

            self.registered = True

            if self.check_password(username, password):
                print("hereeeee!!")
                return True
            else:
                return False # recognition failed

        else: # is registered

            cmd = input("Please enter command:\n").upper()
            tof, msg = Pro.check_cmd(cmd)
            if tof:
                #sending to server
                packet = Pro.create_msg(cmd.encode())
                self.my_socket.send(packet)

                # receiving from server
                self.handle_server_response(cmd)
                if cmd == 'EXIT':
                    return False
            else:
                print("Not a valid command, or missing parameters\n")

            return True

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


def main():
    #client_details = {"username": [], "password": []}  # dictionary

    myclient = Cli()
    myclient.connect("127.0.0.1", Pro.PORT)
    print('Welcome to remote computer application. Available commands are:\n')
    print('START_STREAMING\nSTOP_STREAMING\nEXIT')
    while myclient.donext():
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
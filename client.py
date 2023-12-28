import socket
import pickle
import cv2

from protocol import Pro

BUFFER_SIZE = 4096

class Cli:
    SAVED_PHOTO_LOCATION = r"c:\users\galis\pictures\screenshot.jpg" # The path + filename where the copy of the screenshot at the client should be saved

    def __init__(self):
        # open socket with the server

        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip, port):
        self.my_socket.connect((ip, port))

    def handle_server_response(self, cmd):
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
                print("HELLO")
                #print(msg)
            else:
                print("Error receiving frame from the server.")
                break







        # (10) treat SEND_PHOTO

    def donext(self):
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
            data = self.my_socket.recv(BUFFER_SIZE)
            if not data:
                break
            frame_data += data
        img_encoded = pickle.loads(frame_data)
        frame = cv2.imdecode(img_encoded, cv2.IMREAD_COLOR)
        cv2.imshow('Server Stream', frame)
        cv2.waitKey(1)


    def display_frame(frame):
        cv2.imshow('Server Stream', frame)
        cv2.waitKey(1)




    def close(self):
        self.my_socket.close()


def main():
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
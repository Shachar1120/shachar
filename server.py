import pickle
import socket
import threading

from protocol import Pro
#from camera import Cam

import glob
import os
import shutil
import subprocess
import cv2


class Ser:
    IP = "0.0.0.0"

    def __init__(self, ip, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen()
        print("Server is up and running")
    def accept(self):
        (self.client_socket, self.client_address) = self.server_socket.accept()
        print("Client connected")

    def check_client_request(self, data):
        """
        Break cmd to command and parameters
        Check if the command and params are good.

        For example, the filename to be copied actually exists

        Returns:
            valid: True/False
            command: The requested cmd (ex. "DIR")
            params: List of the cmd params (ex. ["c:\\cyber"])
        """
        # Use protocol.check_cmd first
        tof, msg = Pro.check_cmd(data)
        if tof:
            cmd = data
            if cmd == 'START_STREAMING' or cmd == 'STOP_STREAMING':
                return True, cmd, None

    def donext(self):
        #do next
        # Check if protocol is OK, e.g. length field OK
        valid_protocol, cmd = Pro.get_msg(self.client_socket)#מקבלת פקודה מהלקוח
        print(f"received: {cmd} and validation turn out {valid_protocol}")

        if valid_protocol:
            #Check if params are good,e.g. correct number of params, file name exists
            cmd_str = cmd.decode()
            valid_cmd, command, params = self.check_client_request(cmd_str)
            if valid_cmd:
                #

                # prepare a response using "handle_client_request"
                response = self.handle_client_request(command, params)

                # add length field using "create_msg"
                msg = Pro.create_msg(response.encode())

                if command == 'EXIT':
                    return False
                self.client_socket.send(msg)

                # # (9)
                #
                return True

            else:
                # prepare proper error to client
                response = 'Bad command or parameters'
                # send to client

        else:
            # prepare proper error to client
            response = 'Packet not according to protocol'
            # send to client

            # Attempt to clean garbage from socket
            self.client_socket.recv(1024)



    def handle_client_request(self, command, params):
        """Create the response to the client, given the command is legal and params are OK

        For example, return the list of filenames in a directory
        Note: in case of SEND_PHOTO, only the length of the file will be sent

        Returns:
            response: the requested data

        """
        #global response
        if command == 'START_STREAMING':
            self.camera(command)
        elif command == 'STOP_STREAMING':
            os.remove(params[0])
            response = f"deleted file {params[0]}"

        #return response

    def close(self):
        self.server_socket.close()

    def send_frame(self, frame, client_socket):
        _, img_encoded = cv2.imencode('.jpg', frame)
        frame_data = pickle.dumps(img_encoded)
        frame_msg = Pro.create_msg(frame_data)
        self.client_socket.send(frame_msg)

        #send_thread = threading.Thread(target=frame)
        #send_thread.start()

    def camera(self, command):
        #התחלת לקבל פריימים מהמצלמה
        vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # an object that capture a video from the camera

        while (True):

            # Capture the video frame by frame

            # read function-returns the specified number of bytes from the file.
            # Default is -1 which means the whole file.

            ret, frame = vid.read()
            #self.send_frame(frame, self.my_socket)

            # שליחת הפריים ללקוח
            self.send_frame(frame, self.client_socket)

            # Display the resulting frame
            # cv2.imshow(window_name-name of the window in which image to be displayed. , image-he image that is to be displayed.)

            #cv2.imshow('frame', frame)


            if command == "STOP_STREAMING":
                break

            # the 'q' button is set as the
            # quitting button you may use any
            # desired button of your choice
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # After the loop release the cap object
        vid.release()

def main():
    # open socket with client
    myserver = Ser(Ser.IP, Pro.PORT)
    # (1)
    myserver.accept()
    # handle requests until user asks to exit
    while myserver.donext():
        continue
    # close sockets
    print("Closing connection")
    myserver.close()



if __name__ == '__main__':
    main()
import socket
from protocol import Pro

class Cli:
    SAVED_PHOTO_LOCATION = r"c:\users\galis\pictures\screenshot.jpg" # The path + filename where the copy of the screenshot at the client should be saved

    def _init_(self):
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
        # (8) treat all responses except SEND_PHOTO
        isTrue, msg = Pro.get_msg(self.my_socket)
        if isTrue and not cmd == "SEND_PHOTO":
            print(msg)
        elif cmd == "SEND_PHOTO":
            file_size = int(msg)

            with open(Cli.SAVED_PHOTO_LOCATION, 'wb') as outfile:
                outfile.write(self.my_socket.recv(file_size))
            print("screenshot saved at client")






        # (10) treat SEND_PHOTO

    def donext(self):
        cmd = input("Please enter command:\n").upper()
        tof, msg = Pro.check_cmd(cmd)
        #print("at client")
        if tof:
            #sending to server
            packet = Pro.create_msg(cmd)
            self.my_socket.send(packet.encode())

            # receiving from server
            self.handle_server_response(cmd)
            if cmd == 'EXIT':
                return False
        else:
            print("Not a valid command, or missing parameters\n")

        return True


    def close(self):
        self.my_socket.close()


def main():
    myclient = Cli()
    myclient.connect("192.168.68.69", Pro.PORT)
    print('Welcome to remote computer application. Available commands are:\n')
    print('TAKE_SCREENSHOT\nSEND_PHOTO\nDIR\nDELETE\nCOPY\nEXECUTE\nEXIT')
    while myclient.donext():
        continue
    myclient.close()
    # (2)

    # print instructions


    # my_socket.send(protocol.create_msg(cmd).encode())


    # loop until user requested to exit


if __name__ == '_main_':
    main()
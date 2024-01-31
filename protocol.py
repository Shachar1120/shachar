import os
import socket

# title Untitled
#
# note right of Server: Client connect to server
# Client1->Server: connect ServerSocket
# Server->Client1: ServerSocket accept
#
# note right of Server: Client connect to server
# Client2->Server: connect ServerSocket
# Server->Client2: ServerSocket accept
#
# note right of Client1: initiate call to Client2
# Client1->Server: call client 2
# Server->Client2: client 1 sent code to connect
# Client2->Server: accept code connect of client 1
#
# note right of Server: negotiate call between client 1 and 2
#
# Server->Client1: client2 (ip, port, master)
# Server->Client2: client1 (ip, port, slave)
#
# note right of Client1: connect to client2
# Client1->Client2: connect the call
# Client2->Client1: accept the call
#
# note right of Client1: send frames
# note right of Client2: send frames
# Client1->Client2: send frame 1
# Client2->Client1: send frame 1
# Client2->Client2: present frame 1
# Client1->Client1: present frame 1
#
# Client1->Client2: send frame 2
# Client2->Client1: send frame 2
# Client2->Client2: present frame 2
# Client1->Client1: present frame 2
#
# note right of Client1: ...
# note right of Client2: ...

class Pro:

    LENGTH_FIELD_SIZE = 6
    PORT = 8820

    #cmds:
    REGISTER = "REGISTER"
    CHECK = "CHECK"
    PARAMETERS_DELIMITER = " "


    @staticmethod
    def get_msg(my_socket):
        """
        Extract message from protocol, without the length field
        If length field does not include a number, returns False, "Error"
        """
        msg_len_before_valid = my_socket.recv(Pro.LENGTH_FIELD_SIZE).decode()
        if not msg_len_before_valid.isdecimal():
            return False, "ERROR"

        msg_len = int(msg_len_before_valid)
        message = my_socket.recv(msg_len).decode()
        return True, message


    @staticmethod
    def check_cmd(data: str):
        """
        Check if the command is defined in the protocol, including all parameters
        For example, DELETE c:\work\file.txt is good, but DELETE alone is not
        """
        if data == 'START_STREAMING' or data == 'STOP_STREAMING':
            return True, data
        return False, "Not a valid message"

    @staticmethod
    def create_msg(data: bytes):
        """
        Create a valid protocol message, with length field
        """
        data_len = len(data)
        return str(data_len).zfill(Pro.LENGTH_FIELD_SIZE).encode() + data

    @staticmethod
    def get_msg(my_socket):
        """
        Extract message from protocol, without the length field
        If length field does not include a number, returns False, "Error"
        """
        msg_len_before_valid = my_socket.recv(Pro.LENGTH_FIELD_SIZE)
        msg_len_before_valid = msg_len_before_valid.decode()
        if not msg_len_before_valid.isdecimal():
            return False, "ERROR"

        msg_len = int(msg_len_before_valid)
        message = my_socket.recv(msg_len)
        return True, message

    #
    # @staticmethod
    # def check_file(data):
    #     cmd_structure = data.split(" ")
    #     cmd = cmd_structure[0]
    #     if cmd in ['DIR ', 'DELETE', 'EXECUTE']:
    #         if len(cmd_structure) == 2:
    #             if os.path.exists(cmd[1]):
    #                 return True, cmd[0], cmd[1]
    #         else:
    #             return False, "file doesnt exist"
    #     if cmd in ['COPY']:
    #         if len(cmd_structure) == 3:
    #             if os.path.exists(cmd[1]) and os.path.exists(cmd[2]):
    #                 cmds = cmd[1], cmd[2]
    #                 return True, cmd[0], cmds
    #         else:
    #             return False, "one of the files dont exist"
    #     if data == 'EXIT' or data == 'TAKE_SCREENSHOT' or data == 'SEND_PHOTO':
    #         return True

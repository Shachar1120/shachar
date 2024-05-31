import os
import socket

# title Single Client connect, register, assign
#
# note right of Server: Client connect to server
# Client1->Server: connect ServerSocket
# Server->Client1: ServerSocket accept
#
# note right of Server: Client register to server
# Client1->Server: REGISTER <username> <password>
# Server->Server: check if username exist
#
# note right of Server: Server already has a username(sending Not Ack):
# Server->Client1: RGISTER_NACK
#
# note right of Server: Server validate new username(sending Ack):
# Server->Server: add user to dict of registered
# Server->Client1: RGISTER_ACK
# Client1->Client1: understand client is registered
#
# note right of Server: Client assign to server
# Client1->Server: ASSIGN <username> <password>
# Server->Server: check if username exist and password fit to username
#
# note right of Server: Server wrong password or no username(sending Not Ack):
# Server->Client1: ASSIGN_NACK
#
# note right of Server: Server validate username credentials (sending Ack):
# Server->Server: add user to dict of assigned
# Server->Client1: ASSIGN_ACK <token>
# note right of Client: client assigned


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
    #REGISTER = "REGISTER"
    #CHECK = "CHECK"
    PARAMETERS_DELIMITER = " "
    REGISTER = 0
    REGISTER_ACK = 1
    REGISTER_NACK = 2
    ASSIGN = 3
    ASSIGN_ACK = 4
    ASSIGN_NACK = 5
    CONTACTS = 6
    ASSIGNED_CLIENTS = 7
    CALL = 8
    TARGET_ACK = 9
    TARGET_NACK = 10
    ASK_TARGET_DETAILS = 11
    SEND_TARGET_DETAILS = 12
    RING = 13
    IN_CALL = 14
    FRAME = 15
    cmds = ["REGISTER", "REGISTER_ACK", "REGISTER_NACK", "ASSIGN", "ASSIGN_ACK", "ASSIGN_NACK", "CONTACTS", "ASSIGNED_CLIENTS", "CALL", "TARGET_ACK", "TARGET_NACK", "ASK_TARGET_DETAILS", "SEND_TARGET_DETAILS", "RING", "IN_CALL", "FRAME"]

    @staticmethod
    def get_msg(socket_to_server: socket) -> (bool, str):
        """
        Extract message from protocol, without the length field
        If length field does not include a number, returns False, "Error"
        """

        msg_len_before_valid_bytes = socket_to_server.recv(Pro.LENGTH_FIELD_SIZE)
        if msg_len_before_valid_bytes == None or msg_len_before_valid_bytes == b'':
            return False, "ERROR_SOCEKT_DISCONNECTED"

        msg_len_before_valid = msg_len_before_valid_bytes.decode()
        if not msg_len_before_valid.isdecimal():
            return False, "ERROR_WRONG_PROTOCOL"

        msg_len = int(msg_len_before_valid)
        message_bytes = socket_to_server.recv(msg_len)
        message = message_bytes.decode()
        return True, message # message is string

    @staticmethod
    def check_cmd(cmd: str):
        if cmd in Pro.cmds:
            return True
        return False

    @staticmethod
    def check_register_or_assign(cmd: str):
        return cmd == Pro.cmds[Pro.REGISTER] or cmd == Pro.cmds[Pro.ASSIGN]

    @staticmethod
    def check_contacts(cmd: str):
        return cmd == Pro.cmds[Pro.CONTACTS]

    @staticmethod
    def check_call(cmd: str):
        return cmd == Pro.cmds[Pro.CALL]

    @staticmethod
    def check_call(cmd: str):
        return cmd == Pro.cmds[Pro.CALL]

    @staticmethod
    def check_cmd_and_params(cmd: str, params=[]):
        """
        Check if the command is defined in the protocol, including all parameters
        For example, DELETE c:\work\file.txt is good, but DELETE alone is not
        """
        if Pro.check_register_or_assign(cmd) and len(params) == 3:
            return True, "Valid cmd"
        elif Pro.check_contacts(cmd) and len(params) == 0:
            return True, "Valid cmd"
        elif Pro.check_call(cmd) and len(params) == 1:
            return True, "Valid cmd"
        else:
            return False, "Not a valid cmd"

    @staticmethod
    def create_msg(cmd: bytes, params=[]) -> bytes:
        """
        Create a valid protocol message, with length field
        """
        len_params = len(params)
        if len_params == 0:
            msg_to_send = Pro.PARAMETERS_DELIMITER.encode().join([cmd] + [str(len_params).encode()])
        else:
            msg_to_send = Pro.PARAMETERS_DELIMITER.encode().join([cmd] + [str(len_params).encode()] + params)
        msg_len = len(msg_to_send)
        return str(msg_len).zfill(Pro.LENGTH_FIELD_SIZE).encode() + msg_to_send

    # @staticmethod
    # def get_msg(socket_to_server):
    #     """
    #     Extract message from protocol, without the length field
    #     If length field does not include a number, returns False, "Error"
    #     """
    #     msg_len_before_valid = socket_to_server.recv(Pro.LENGTH_FIELD_SIZE)
    #     msg_len_before_valid = msg_len_before_valid.decode()
    #     if not msg_len_before_valid.isdecimal():
    #         return False, "ERROR"
    #
    #     msg_len = int(msg_len_before_valid)
    #     message = socket_to_server.recv(msg_len)
    #     return True, message
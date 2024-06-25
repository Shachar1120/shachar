import pickle
import socket
from new_protocol import Pro
import select
import pyaudio
from AudioHandling import AudioHandling
from call_utilities import *

class NetworkHandling:
    def __init__(self, socket_to_server, profile, move_to_ringing_acceptor):
        self.socket_to_server = socket_to_server
        self.call_initiate_socket = None
        self.call_accept_socket = None
        self.profile = profile
        self.audio_handler_obj = None
        self.on_ring_func = None
        self.in_call_func = None
        self.on_contact_func = None
        self.move_to_ringing_acceptor = move_to_ringing_acceptor
        self.contacts_obj = None
        self.in_call = False



    def init_network(self, contacts_obj):
        self.contacts_obj = contacts_obj
        # open socket with the server
        self.call_initiate_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.call_accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.call_accept_socket.bind(("0.0.0.0", self.profile.call_accept_port))
        self.call_accept_socket.listen()

    def register_on_ring(self, func):
        self.on_ring_func = func

    def register_in_call(self, func):
        self.in_call_func = func
        ################################
        # network ==> responder ... secondary thread
        ################################

    def register_on_contact(self, func):
        self.on_contact_func = func

    def handle_updated_assigned_clients(self, assigned_clients):
        if self.contacts_obj:
            self.contacts_obj.update_contacts(assigned_clients)

    def wait_for_network(self):

        CHUNK = 4096
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 10

        while True:
            # אלגוריתם להמתנה להודעות מהרשת, וטיפול בהודעות על פי יעדן
            rlist, _, _ = select.select([self.socket_to_server, self.call_initiate_socket, self.call_accept_socket],
                                        [], [], 0.01)

            for s in rlist:
                if s == self.socket_to_server:  # connect with server
                    res, message = Pro.get_msg(self.socket_to_server)
                    if res:
                        opcode, nof_params, params = Pro.split_message(message)
                        if opcode == "ASSIGNED_CLIENTS":
                            print("networkhandeling got contacts")
                            self.assigned_clients_dict = pickle.loads(params[0])
                            print("dict in networkhandeling!!!", self.assigned_clients_dict)
                            self.handle_updated_assigned_clients(self.assigned_clients_dict)

                elif s == self.call_accept_socket:  # for call establishment
                    self.call_initiate_socket, _ = self.call_accept_socket.accept()
                    print("Client connected")

                elif s == self.call_initiate_socket:  # for call handling

                    res, message = Pro.get_msg(s)
                    #print(f"wait_for_network: {message}")
                    if res:
                        opcode, nof_params, params = Pro.split_message(message)

                        #print("the message is:", opcode, nof_params, params)

                        if opcode == "MOVE_TO_CONTACT":
                            self.in_call = False
                            print("received MOVE_TO_CONTACT")
                            self.on_contact_func()
                            s.close()
                            self.call_initiate_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            break
                        if opcode == "RING":
                            params = params[0].decode()
                            print("received call")
                            # tkinter after
                            self.on_ring_func()
                            # self.init_panel_acceptor_create()

                        elif opcode == "IN_CALL":
                            self.in_call = True
                            # params = params[0].decode()
                            print("got in call!! AudioHandling")

                            if self.audio_handler_obj is None:
                                self.audio_handler_obj = AudioHandling(self.profile)
                                self.audio_handler_obj.init_channels()

                            self.in_call_func()

                        elif opcode == "FRAME":
                            if self.audio_handler_obj is not None:
                                data = params[0]
                                #print("FRAME params!!! (data)", params)
                                # accept frame and play
                                data = Pro.PARAMETERS_DELIMITER.encode().join(params) # split msg broke the pickle data by PARAMETERS_DELIMITER, so we combined it bak
                                # data = pickle.loads(data)
                                #print(f"got frame: {data}")
                                self.audio_handler_obj.put_frame(data)
                        else:
                            pass

                    else:
                        pass
                        #print("wrong user! you called yourself") # bug- when calling userself(we will fi it by remoing ourself from contacts list)


            if self.audio_handler_obj is not None and self.in_call:
                #if (self.audio_handler_obj):
                #   print(f"self.audio_handler_obj = {self.audio_handler_obj}, self.audio_handler_obj.stream_input = {self.audio_handler_obj.stream_input}")
                # audio handling... if in call
                if self.audio_handler_obj is not None and self.audio_handler_obj.stream_input is not None:
                    data = self.audio_handler_obj.get_frame()

                    cmd = Pro.cmds[Pro.FRAME].encode()
                    # params = [pickle.dumps(data)]
                    params = [data]
                    msg_to_send = Pro.create_msg(cmd, params)
                    self.call_initiate_socket.send(msg_to_send)

    def set_audio_handler(self, audio_handler_obj):
        self.audio_handler_obj = audio_handler_obj

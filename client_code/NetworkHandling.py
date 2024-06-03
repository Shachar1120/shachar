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
        self.move_to_ringing_acceptor = move_to_ringing_acceptor

    def init_network(self):
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

    def wait_for_network(self):

        CHUNK = 4096
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 10

        while True:
            rlist, _, _ = select.select([self.socket_to_server, self.call_initiate_socket, self.call_accept_socket],
                                        [], [], 0.01)

            for s in rlist:
                if s == self.socket_to_server:  # connect with server
                    pass
                elif s == self.call_accept_socket:  # for call establishment
                    self.call_initiate_socket, _ = self.call_accept_socket.accept()
                    print("Client connected")

                elif self.call_initiate_socket:  # for call handling

                    res, message = Pro.get_msg(self.call_initiate_socket)
                    print(f"wait_for_network: {message}")
                    opcode, nof_params, params = Pro.split_message(message)
                    if res:
                        print("the message is:", opcode, nof_params, params)

                        if opcode == "RING":
                            params = params[0].decode()
                            print("received call")
                            # tkinter after
                            self.on_ring_func()
                            # self.init_panel_acceptor_create()

                        elif opcode == "IN_CALL":
                            # params = params[0].decode()
                            print("got in call!!")
                            self.in_call_func()
                            if self.audio_handler_obj is None:
                                self.audio_handler_obj = AudioHandling(self.profile)

                            self.state = CallStates.IN_CALL
                            self.transition = True





                        elif opcode == "FRAME":
                            data = params[0]
                            print("FRAME params!!! (data)", params)
                            # accept frame and play
                            # data = Pro.PARAMETERS_DELIMITER.encode().join(params) # split msg broke the pickle data by PARAMETERS_DELIMITER, so we combined it bak
                            # data = pickle.loads(data)
                            print(f"got frame: {data}")
                            self.audio_handler_obj.put_frame(data)
                            pass

                        else:
                            pass

                    else:
                        print("didnt get the message")

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


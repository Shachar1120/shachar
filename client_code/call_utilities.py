
class CallStates:
    INIT = 0
    RINGING = 1
    IN_CALL = 2

class UserProfile:
    # your_port == call_initiate_port
    # my_port == call_accept_port
    def __init__(self, call_accept_port, call_initiate_port, my_mic, my_speaker):
        self.call_accept_port = call_accept_port
        self.call_initiate_port = call_initiate_port
        self.my_mic = my_mic
        self.my_speaker = my_speaker

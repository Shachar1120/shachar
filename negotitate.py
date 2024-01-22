class ClientRole:
    MASTER = 1
    SLAVE = 2
    A=3

class ClientDetails:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class ClientRole:
    MASTER = 1
    SLAVE = 2

class ClientDetails:
    def __init__(self, username, password):
        self.username = username
        self.password = password

import threading
import time
import socket

class ExampleObj:
    def __init__(self, a):
        self.a = a
        self.server_socket = socket.socket() #self.sock_initiate_call
        self.server_socket.bind(("0.0.0.0", 2000))
        self.server_socket.listen()
        self.client_socket = None
    # פונקציה זו תופעל בתהליך נפרד
    def print_numbers(self):
        for i in range(1, 100):
            print("Number:", self.a)
            self.client_socket, _ = self.server_socket.accept()
            time.sleep(1)  # המתנה לשנייה בין כל הדפסה


eobj = ExampleObj(5)
# יצירת תהליך חדש שיפעיל את הפונקציה print_numbers
thread = threading.Thread(target=eobj.print_numbers)

# הפעלת התהליך
thread.start()

# המשך התוכנית הראשית לרוץ ולהדפיס הודעה
for _ in range(100):
    eobj.a += 1
    if eobj.client_socket is not None:
        print("client connected!")
    print("Main Thread is running...")
    time.sleep(1)  # המתנה לשנייה

# המתנה לסיום התהליך הנפרד
thread.join()

print("Main Thread finished.")

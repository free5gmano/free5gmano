import socket


class CommandOutputSocket(socket.socket):
    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        bind_ip = "0.0.0.0"
        bind_port = 8888
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((bind_ip, bind_port))
        self.listen(2)
        self.settimeout(30)
        print("[*] Listening on " + bind_ip + ":" + str(bind_port))

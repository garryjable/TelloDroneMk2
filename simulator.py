import socket
import threading


class DroneSimulator:

    #    _host = "127.0.0.1"
    #    _host = '192.168.10.1'
    #    _port = 8891

    def __init__(self, host=None, port=None):
        self.commands = {
            "command": lambda params: self.handleCommand(params),
            "takeoff": lambda params: self.handleTakeoff(params),
            "land": lambda params: self.handleLand(params),
            "up": lambda params: self.handleUp(params),
            "right": lambda params: self.handleRight(params),
            "down": lambda params: self.handleDown(params),
            "left": lambda params: self.handleLeft(params),
        }

        # from test server
        host = "127.0.0.1"
        port = 8889

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((host, port))
        self._socket.settimeout(15)

        # from drone dispatcher
        #        local_host = ""
        #        if host:
        #            self._host = host
        #        if port:
        #            self._port = port
        #        self._drone = (self._host, self._port)
        #        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #        self._socket.bind((local_host, self._port + 1))
        return

    def close_socket(self):
        self._socket.close()

    def __del__(self):
        try:
            self._socket.close()
        except AttributeError:
            return

    def start_listening(self):
        self.thread = threading.Thread(target=self.listen_for_command)
        self.thread.start()
        return self.thread

    def listen_for_command(self):
        while getattr(self.thread, "do_run", True):
            data, addr = self._socket.recvfrom(1024)
            print("message from: " + str(addr))
            print("from connect user: " + str(data.decode()))
            data = str(data.decode())
            args = data.split(" ")
            print('here be args')
            print(args)
            try:
                response = self.commands[args[0]](args)
            except AttributeError:
                response = "error"
            print("sending: " + str(response))
            self._socket.sendto(data.encode(), addr)

    def stop_listening(self):
        self.thread.do_run = False
        self.thread.join()

    def handleCommand(self, args):
        return "ok"

    def handleTakeoff(self, args):
        return "ok"

    def handleLand(self, args):
        return "ok"

    def handleUp(self, args):
        return "ok"

    def handleRight(self, args):
        return "ok"

    def handleDown(self, args):
        return "ok"

    def handleLeft(self, args):
        return "ok"

    def handleLeft(self, args):
        return "ok"


# class DroneMonitor:
#    _host = "127.0.0.1"
#    #    _host = '192.168.10.1'
#    _port = 8891
#
#    def __init__(self, host=None, port=None):
#        local_host = ""
#        if host:
#            self._host = host
#        if port:
#            self._port = port
#        self._drone = (self._host, self._port)
#        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        self._socket.bind((local_host, self._port + 1))
#        return
#
#    def close_socket(self):
#        self._socket.close()
#
#    def __del__(self):
#        try:
#            self._socket.close()
#        except AttributeError as e:
#            return
#
#    def listen_for_status_update(self, mission):
#        #print("Server Started")
#        #while True:
#        #    data, addr = s.recvfrom(1024)
#        #    print("message from: " + str(addr))
#        #    print("from connect user: " + str(data.decode()))
#        #    data = str(data.decode()))
#        #    args = data.split(' ')
#        #    try:
#        #        response = commands[args[0]](args)
#        #    except:
#        #        response = "error"
#        #    print("sending: " + str(response))
#        #    s.sendto(data.encode(), addr)
#        #s.close()
#        print("listening")

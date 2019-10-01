import socket

class DroneSimulator:

    commands = {
            "command": lambda params: handleCommand(params),
            "takeoff": lambda params: handleTakeoff(params),
            "land": lambda params: handleLand(params),
            "up": lambda params: handleUp(params),
            "right": lambda params: handleRight(params),
            "down": lambda params: handleDown(params),
            "left": lambda params: handleLeft(params),
    }

    _host = "127.0.0.1"
    #    _host = '192.168.10.1'
    _port = 8891

    def __init__(self, host=None, port=None):

# from test server
#        host = "127.0.0.1"
#        port = 8889
#
#        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        s.bind((host, port))


#from drone dispatcher
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
        except AttributeError as e:
            return

    def listen_for_command(self, mission):
        #print("Server Started")
        #while True:
        #    data, addr = s.recvfrom(1024)
        #    print("message from: " + str(addr))
        #    print("from connect user: " + str(data.decode()))
        #    data = str(data.decode()))
        #    args = data.split(' ')
        #    try:
        #        response = commands[args[0]](args)
        #    except:
        #        response = "error" 
        #    print("sending: " + str(response))
        #    s.sendto(data.encode(), addr)
        #s.close()
        print("listening")

    def handle_command(self, mission):
        print("handling")

    def _send_response(self, message): # method that handles sending messages to drone
        self._socket.sendto(message.encode(), self._drone)
        data, addr = self._socket.recvfrom(1024)
        return "Recieved from server: " + str(data.decode())


class DroneMonitor:
    _host = "127.0.0.1"
    #    _host = '192.168.10.1'
    _port = 8891

    def __init__(self, host=None, port=None):
        local_host = ""
        if host:
            self._host = host
        if port:
            self._port = port
        self._drone = (self._host, self._port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((local_host, self._port + 1))
        return

    def close_socket(self):
        self._socket.close()

    def __del__(self):
        try:
            self._socket.close()
        except AttributeError as e:
            return

    def listen_for_status_update(self, mission):
        #print("Server Started")
        #while True:
        #    data, addr = s.recvfrom(1024)
        #    print("message from: " + str(addr))
        #    print("from connect user: " + str(data.decode()))
        #    data = str(data.decode()))
        #    args = data.split(' ')
        #    try:
        #        response = commands[args[0]](args)
        #    except:
        #        response = "error" 
        #    print("sending: " + str(response))
        #    s.sendto(data.encode(), addr)
        #s.close()
        print("listening")

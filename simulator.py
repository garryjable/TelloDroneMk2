import socket
import threading
from models import DroneStatusStore
import time


class DroneSimulator:

    def __init__(self):
        self.commands = {
            "command": lambda params: self.handleCommand(params),
            "takeoff": lambda params: self.handleTakeoff(params),
            "land": lambda params: self.handleLand(params),
            "up": lambda params: self.handleUp(params),
            "right": lambda params: self.handleRight(params),
            "down": lambda params: self.handleDown(params),
            "left": lambda params: self.handleLeft(params),
        }
        self.speed = 10
        host = "127.0.0.1"
        port = 8889
        status_host = "0.0.0.0"
        status_port = 8890
        self.status_store = DroneStatusStore()
        self.thread = None
        self.report_thread = None
        self.status_addr = (status_host, status_port)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((host, port))
        self._socket.settimeout(15)

        self._status_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._status_socket.bind(self.status_addr)
        self._status_socket.settimeout(15)

        self.start_reporting()
        
        return

    def close_socket(self):
        self._socket.close()

    def __del__(self):
        self.stop_reporting()
        try:
            self._socket.close()
        except AttributeError:
            return

    def start_reporting(self):
        self.report_thread = threading.Thread(target=self.report_status)
        self.report_thread.start()
        return self.report_thread

    def report_status(self):
        while getattr(self.report_thread, "do_run", True):
            latest_status = self.status_store.get_latest_status()
            self._socket.sendto(latest_status.encode(), self.status_addr)
            time.sleep(.1)

    def stop_reporting(self):
        self.report_thread.do_run = False
        self.report_thread.join()

    def start_listening(self):
        self.thread = threading.Thread(target=self.listen_for_command)
        self.thread.start()
        return self.thread

    def listen_for_command(self):
        while getattr(self.thread, "do_run", True):
            try:
                data, addr = self._socket.recvfrom(1024)
            except socket.timeout:
                print("sending: " + "landing")
                return
            else:
                print("message from: " + str(addr))
                print("from connect user: " + str(data.decode()))
                data = str(data.decode())
                args = data.split(" ")
                print('here be args')
                print(args)
                try:
                    response = self.commands[args[0]](args)
                except AttributeError as e:
                    print(e)
                    response = "error"
                print("sending: " + str(response))
                self._socket.sendto(data.encode(), addr)

    def stop_listening(self):
        self.thread.do_run = False
        self.thread.join()

    def handleCommand(self, args):
        return "ok"

    def handleTakeoff(self, args):
        distance = 50
        axis = 'vgz'
        direction = 1
        return self.handleBaseMovement(axis, direction, distance)

    def handleLand(self, args):
        status = self.status_store.get_latest_status_dict()
        distance = int(status['h'])
        axis = 'vgz'
        direction = -1
        return self.handleBaseMovement(axis, direction, distance)

    def handleUp(self, args):
        distance = int(args[1])
        axis = 'vgz'
        direction = 1
        return self.handleBaseMovement(axis, direction, distance)

    def handleRight(self, args):
        distance = int(args[1])
        axis = 'vgx'
        direction = 1
        return self.handleBaseMovement(axis, direction, distance)

    def handleDown(self, args):
        distance = int(args[1])
        axis = 'vgz'
        direction = -1
        return self.handleBaseMovement(axis, direction, distance)

    def handleLeft(self, args):
        distance = int(args[1])
        axis = 'vgx'
        direction = -1
        return self.handleBaseMovement(axis, direction, distance)

    def handleBaseMovement(self, axis, direction, distance):
        status = self.status_store.get_latest_status_dict()
        status[axis] = direction * self.speed
        self.status_store.update_latest_status_with_dict(status)
        time.sleep(distance/ self.speed)
        status[axis] = 0
        if axis == 'vgz':
            status['h'] += direction * distance
        self.status_store.update_latest_status_with_dict(status)
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

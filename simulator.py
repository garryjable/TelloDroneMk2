import socket
import threading
from models import DroneStatusStore
import time


class DroneSimulator:

    def __init__(self, commands=None):
        self.commands = {
            "command": lambda params, base_handler: handleCommand(params, base_handler),
            "takeoff": lambda params, base_handler: handleTakeoff(params, base_handler),
            "land": lambda params, base_handler: handleLand(params, base_handler),
            "up": lambda params, base_handler: handleUp(params, base_handler),
            "right": lambda params, base_handler: handleRight(params, base_handler),
            "down": lambda params, base_handler: handleDown(params, base_handler),
            "left": lambda params, base_handler: handleLeft(params, base_handler),
        }
        if commands: 
            self.commands = commands
        self.speed = 10
        host = "127.0.0.1"
        port = 8889
        status_host = "127.0.0.1"
        status_port = 8890
        self.status_store = DroneStatusStore()
        self.thread = None
        self.report_thread = None
        self.status_addr = (status_host, status_port)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((host, port))
        self._socket.settimeout(15)

        self._status_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._status_socket.bind((host,8895))
        self._status_socket.settimeout(15)

        self.start_reporting()
        
        return

    def close_socket(self):
        self._socket.close()
        self._status_socket.close()

    def __del__(self):
        self.stop_reporting()
        try:
            self._socket.close()
            self._status_socket.close()
        except AttributeError:
            return

    def start_reporting(self):
        self.report_thread = threading.Thread(target=self.report_status)
        self.report_thread.start()
        return self.report_thread

    def report_status(self):
        start = time.time()
        latest_status_dict = self.status_store.get_latest_status_dict()
        latest_status_dict['time'] = 0
        self.status_store.update_latest_status_with_dict(latest_status_dict)
        while getattr(self.report_thread, "do_run", True):
            latest_status_dict = self.status_store.get_latest_status_dict()
            latest_status_dict['time'] = int(time.time() - start)
            self.status_store.update_latest_status_with_dict(latest_status_dict)
            latest_status = self.status_store.get_latest_status()
            self._status_socket.sendto(latest_status.encode(), self.status_addr)
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
                print("recieved command: " + str(data.decode()))
                data = str(data.decode())
                args = data.split(" ")
                print(args)
                try:
                    response = self.commands[args[0]](args, self.handleBaseMovement)
                except AttributeError as e:
                    print(e)
                    response = "error"
                print("sending: " + str(response))
                self._socket.sendto(data.encode(), addr)

    def stop_listening(self):
        self.thread.do_run = False
        self.thread.join()

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


def handleCommand(args, handleBaseMovement):
    return "ok"

def handleTakeoff(args, handleBaseMovement):
    distance = 50
    axis = 'vgz'
    direction = 1
    return handleBaseMovement(axis, direction, distance)

def handleLand(args, handleBaseMovement):
    status = self.status_store.get_latest_status_dict()
    distance = int(status['h'])
    axis = 'vgz'
    direction = -1
    return handleBaseMovement(axis, direction, distance)

def handleUp( args, handleBaseMovement):
    distance = int(args[1])
    axis = 'vgz'
    direction = 1
    return handleBaseMovement(axis, direction, distance)

def handleRight(args, handleBaseMovement):
    distance = int(args[1])
    axis = 'vgx'
    direction = 1
    return handleBaseMovement(axis, direction, distance)

def handleDown(args, handleBaseMovement):
    distance = int(args[1])
    axis = 'vgz'
    direction = -1
    return handleBaseMovement(axis, direction, distance)

def handleLeft(args, handleBaseMovement):
    distance = int(args[1])
    axis = 'vgx'
    direction = -1
    return handleBaseMovement(axis, direction, distance)


class DroneMonitor:
    _host = "127.0.0.1"
    _port = 8892

    def __init__(self, host=None, port=None):
        local_host = ""
        if host:
            self._host = host
        if port:
            self._port = port
        self.status_port = 8890
        self.status_store = DroneStatusStore()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((local_host, self.status_port))
        self._socket.settimeout(15)
        self.start_listening()
        return

    def close_socket(self):
        self._socket.close()

    def __del__(self):
        self.stop_listening()
        try:
            self._socket.close()
        except AttributeError as e:
            return

    def start_listening(self):
        self.thread = threading.Thread(target=self.listen_for_status)
        self.thread.start()
        return self.thread

    def listen_for_status(self):
        while getattr(self.thread, "do_run", True):
            try:
                status, addr = self._socket.recvfrom(1024)
            except socket.timeout:
                print("lost connection")
                return
            else:
                self.status_store.update_latest_status(status.decode())

    def stop_listening(self):
        self.thread.do_run = False
        self.thread.join()



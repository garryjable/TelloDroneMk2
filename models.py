import socket
import time
from abc import ABC, abstractmethod
import types


class DroneDispatcher:
    _host = "127.0.0.1"
    #    _host = '192.168.10.1'
    _port = 8889

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

    def set_host(self, new_host):
        self._host = new_host

    def set_port(self, new_port):
        self._port = new_port

    def get_port(self):
        return self._port

    def get_host(self):
        return self._host

    def send_drone_on_mission(self, mission):
        mission_flyer = MissionFlyer(lambda self, send_method: mission.execute(send_method)) # passing a mission flying strategy to a flyer
        return mission_flyer.execute(self._send_message)

    def _send_message(self, message): # method that handles sending messages to drone
        self._socket.sendto(message.encode(), self._drone)
        data, addr = self._socket.recvfrom(1024)
        return "Recieved from server: " + str(data.decode())

class MissionLibrary:
    _missions = {}

    def __init__(self, missions=None):
        if missions:
            self._missions = missions

    def get_mission_names(self):
        names = []
        for key, val in self._missions.items():
            names.append(key)
        return names

    def get_mission(self, name):
        try:
            return self._missions[name]
        except KeyError as error:
            return "invalid mission"

    def add_missions(self):
        return

class MissionFlyer:

    def __init__(self, func=None):
        if func is not None:
            self.execute = types.MethodType(func, self)
            self.name = '{}_{}'.format(self.__class__.__name__, func.__name__)
        else:
            self.name = '{}_default'.format(self.__class__.__name__)

    def fly_mission(self, send_method):
        pass

class MissionFactory:

    def create_missions(self, mission_data):
        missions = {}
        for data_obj in mission_data.data:
            if data_obj["type"] == "fast":
                mission = FastMission(data_obj["commands"], data_obj["name"])
            elif data_obj["type"] == "slow":
                mission = SlowMission(data_obj["commands"], data_obj["name"])
            elif data_obj["type"] == "verbosefast":
                mission = VerboseFastMission(data_obj["commands"], data_obj["name"])
            missions[data_obj["name"]] = mission
        return missions

    def create_missions_from_file(self, mission_data):
        pass

    def parse_json(self, mission_data):
        pass

    def parse_py(self, mission_data):
        pass

    def parse_csv(self, mission_data):
        pass

class Mission(ABC):
    _name = "default mission"
    _commands = []

    def __init__(self, command_list, name):
        self._commands = command_list
        self._name = name

    def execute(self, send_method): # template method
        self._start_mission(send_method)
        self._execute_commands(send_method)
        self._end_mission(send_method)
        return "you flew mission " + self._name

    def _start_mission(self, send_method):
        send_method('takeoff')
        send_method('command')
        send_method('command')
        send_method('command')

    @abstractmethod
    def _execute_commands(self, send_method):
        pass

    def _end_mission(self, send_method):
        send_method('takeoff')


class FastMission(Mission):

    def _execute_commands(self, send_method):
        for command in self._commands:
            send_method(command)
            time.sleep(3)


class SlowMission(Mission):
    def _execute_commands(self, send_method):
        for command in self._commands:
            send_method(command)
            time.sleep(5)


class VerboseFastMission(Mission):
    def _execute_commands(self, send_method):
        for command in self._commands:
            print(send_method(command))
            time.sleep(3)


class Menu:

    def __init__(self, methods):
        self.menu = {
                'help': lambda: self._print_options(),
                'ls': lambda: self._list_missions(methods['ls']),
                'load': lambda: self._list_missions(methods['load']),
                'set port': lambda: self._set_new_value(methods['set port']),
                'set host': lambda: self._set_new_value(methods['set host']),
                'get port': lambda: self._display_info(methods['get port']),
                'get host': lambda: self._display_info(methods['get host']),
                'get host': lambda: self._display_info(methods['get host']),
                'mission': lambda message: methods['mission'](message),
                }

    def _list_missions(self, get_missions_method):
        print("Availible missions:")
        for name in get_missions_method():
            print("                {}".format(name))

    def _load_missions(self, load_missions_method):
        print("Enter path to the file")
        file_path = input("-> ")
        load_missions_method(file_path)

    def _set_new_value(self, set_method):
        print("enter a new value")
        new_value = input("-> ")
        set_method(new_value)

    def _display_info(self, display_info_method):
        info = display_info_method()
        print("current value: {}".format(info))

    def _print_options(self):
        print("enter 'q' to quit")
        print("enter mission name to fly a mission")
        print("enter 'ls' to list possible missions")
        print("enter 'load' to load new missions ")
        print("enter 'set port' to set new port")
        print("enter 'set host' to set new host")
        print("enter 'get port' to get current port value")
        print("enter 'get host' to get current host value")

    def display_menu(self):
        print(
            "Welcome to the tello drone client, enter 'help' for available options, enter 'q' to quit"
        )
        message = input("-> ")
        while message != "q":
            try:
                self.menu[message]()
            except KeyError:
                mission = self.menu['load mission'](message)
                response = self.menu['mission'](mission)
                print(response)
            message = input("-> ")

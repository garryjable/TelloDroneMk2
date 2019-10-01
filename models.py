import socket
import time
from abc import ABC, abstractmethod
import types
import csv
import json


class DroneDispatcher:
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

    def add_missions(self, missions):
        for key, val in missions.items():
            self._missions[key] = val
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


class DroneStatusStore:
    _latest_status = {
            "pitch": 0,
            "roll": 0,
            "yaw": 0,
            "vgx": 0,
            "vgy": 0,
            "vgz": 0,
            "templ": 0,
            "temph": 0,
            "tof": 0,
            "h": 0,
            "bat": 100,
            "baro": 0.00,
            "time": 0,
            "agx": 0.00,
            "agy": 0.00,
            "agz": 0.00,
            }

    def get_latest_status(self):
        status_message = ""
        for key, val in self._latest_status.items():
            if isinstance(val, int):
                val = "%d" % val
            elif isinstance(val, float):
                val = "%.2f" % val
            status_message += "{}:{};".format(key, val)
        status_message += "\r\n"
        return status_message

    def update_latest_status(self, new_status):
        key_val_pairs = new_status.split(';')
        for pair in key_val_pairs:
            try:
                key, val = pair.split(':')
                try: 
                    self._latest_status[key] = val
                except KeyError:
                    print("bad")
                    pass
            except ValueError:
                print("terrible")
                pass

    def get_latest_status_dict(self):
        return self._latest_status

    def update_latest_status_with_dict(self, new_status):
        try:
            for key, val in new_status.items():
                try: 
                    self._latest_status[key] = val
                except KeyError:
                    print("bad")
                    pass
        except ValueError:
            print("terrible")
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

    def create_missions_from_file(self, file_path):
        extension = file_path.split('.')[-1]
        if extension == 'csv':
            return self.parse_csv(file_path)
        elif extension == 'json':
            return self.parse_json(file_path)
        else:
            print("file type could not be recognized")
            return

    def parse_json(self, file_path):
        missions = {}
        with open(file_path) as json_data:
            mission_data = json.load(json_data)
            missions = {}
            for data_obj in mission_data['data']:
                if data_obj["type"] == "fast":
                    mission = FastMission(data_obj["commands"], data_obj["name"])
                elif data_obj["type"] == "slow":
                    mission = SlowMission(data_obj["commands"], data_obj["name"])
                elif data_obj["type"] == "verbosefast":
                    mission = VerboseFastMission(data_obj["commands"], data_obj["name"])
                missions[data_obj["name"]] = mission
            json_data.close()
            return missions

    def parse_csv(self, mission_data):
        missions = {}
        with open(mission_data, 'r') as csvfile:
            mission_data_reader = csv.reader(csvfile, delimiter=',')
            for row in mission_data_reader:
                mission = None
                if row[2].strip() == "fast":
                    mission = FastMission(row[1].split('|'), row[0])
                elif row[2].strip() == "slow":
                    mission = SlowMission(row[1].split('|'), row[0])
                elif row[2].strip() == "verbosefast":
                    mission = VerboseFastMission(row[1].split('|'), row[0])
                if mission:
                    missions[row[0]] = mission
        return missions

class Mission(ABC):
    _name = "default mission"
    _commands = []

    def __init__(self, command_list, name):
        self._commands = command_list
        self._name = name

    def execute(self, send_method): # template method
        self._start(send_method)
        self._execute_commands(send_method)
        self._end(send_method)
        return "you flew mission " + self._name

    def _start(self, send_method):
        send_method('takeoff')
        send_method('command')
        send_method('command')
        send_method('command')

    @abstractmethod
    def _execute_commands(self, send_method):
        pass

    def _end(self, send_method):
        send_method('takeoff')


class FastMission(Mission):

    def _execute_commands(self, send_method):
        for command in self._commands:
            send_method(command)
            time.sleep(.3)


class SlowMission(Mission):
    def _execute_commands(self, send_method):
        for command in self._commands:
            send_method(command)
            time.sleep(.5)


class VerboseFastMission(Mission):
    def _execute_commands(self, send_method):
        for command in self._commands:
            print(send_method(command))
            time.sleep(.3)


class Menu:

    def __init__(self, methods):
        self.menu = {
                'help': lambda: self._print_options(),
                'ls': lambda: self._list_missions(methods['ls']),
                'load': lambda: self._load_missions(methods['load'], methods['save missions']),
                'set port': lambda: self._set_new_value(methods['set port']),
                'set host': lambda: self._set_new_value(methods['set host']),
                'get port': lambda: self._display_info(methods['get port']),
                'get host': lambda: self._display_info(methods['get host']),
                'get host': lambda: self._display_info(methods['get host']),
                'mission': lambda name: methods['mission'](name),
                'get mission': methods['get mission'],
                }

    def _list_missions(self, get_missions_method):
        print("Availible missions:")
        for name in get_missions_method():
            print("                {}".format(name))

    def _load_missions(self, load_missions_method, save_missions_method):
        print("Enter path to the file")
        file_path = input("-> ")
        missions = load_missions_method(file_path)
        save_missions_method(missions)

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
                mission = self.menu['get mission'](message)
                response = self.menu['mission'](mission)
                print(response)
            message = input("-> ")

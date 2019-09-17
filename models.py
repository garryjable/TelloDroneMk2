import socket
import time
from abc import ABC, abstractmethod


class DroneDispatcher:
    _host = "127.0.0.1"
    #    _host = '192.168.10.1'
    _port = 8889
    _missions = {}

    def __init__(self, missions=None, host=None, port=None):
        local_host = ""
        if missions:
            self._missions = missions
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

    def get_mission_names(self):
        names = []
        for key, val in self._missions.items():
            names.append(key)
        return names

    def add_missions(self):
        return

    def send_drone_on_mission(self, name):
        try:
            mission = self._missions[name]
            return mission.execute_commands(self._send_command)
        except KeyError as e:
            return "invalid mission"

    def _send_command(self, command):
        self._socket.sendto(command.encode(), self._drone)
        data, addr = self._socket.recvfrom(1024)
        return "Recieved from server: " + str(data.decode())


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
        command_list.insert(0, "takeoff")
        command_list.insert(0, "command")
        command_list.append("land")
        self._commands = command_list
        self._name = name

    def execute_commands(self, send_method):
        for command in self._commands:
            self._execute_command(command, send_method)
        return "you flew mission " + self._name

    @abstractmethod
    def _execute_command(self, command, send_method):
        pass


class FastMission(Mission):
    def _execute_command(self, command, send_method):
        send_method(command)
        time.sleep(3)


class SlowMission(Mission):
    def _execute_command(self, command, send_method):
        send_method(command)
        time.sleep(5)


class VerboseFastMission(Mission):
    def _execute_command(self, command, send_method):
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
            except AttributeError:
                response = self._dispatcher.send_drone_on_a_mission(message)
                print(response)
            message = input("-> ")

import socket
import time
from abc import ABC, abstractmethod


class DroneDispatcher:
    _host = "127.0.0.1"
    #    _host = '192.168.10.1'
    _port = 8889

    def __init__(self, missions, host=None, port=None):
        local_host = ""
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

    def get_info(self):
        return (self._host, self._port)

    def get_mission_names(self):
        names = []
        for key, val in self._missions.items():
            names.append(key)
        return names

    def fly_mission(self, name):
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
        send_method(command)
        time.sleep(0.01)


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


class ClientCli:
    _dispatcher = None

    def _init_dispatcher(self, missions, host=None, drone_port=None):
        self._dispatcher = DroneDispatcher(missions, host, drone_port)

    def _get_missions(self):
        import mission_data

        mission_factory = MissionFactory()
        return mission_factory.create_missions(mission_data)

    def _list_missions(self):
        print("Availible missions:")
        for name in self._dispatcher.get_mission_names():
            print("                " + name)

    def start_client(self):
        self._init_dispatcher(self._get_missions())
        print(
            "Welcome to the tello drone client, enter 'help' for available options, enter 'q' to quit"
        )
        message = input("-> ")
        while message != "q":
            if message == "help":
                print("enter 'q' to quit")
                print("enter mission name to fly a mission")
                print("enter 'ls' to list possible missions")
                print("enter 'set port' to set new port")
                print("enter 'set host' to set new host")
                print("enter 'info' to get current host and port data")
            elif message == "ls":
                self._list_missions()
            elif message == "set host":
                print("enter new host address")
                message = input("-> ")
                self._dispatcher.set_host(message)
            elif message == "set port":
                message = input("-> ")
                print("enter new port")
                self._dispatcher.set_port(message)
            elif message == "info":
                host, port = self.dispatcher.get_info(message)
                print("current host: " + host)
                print("current port: " + port)
            else:
                response = self._dispatcher.fly_mission(message)
                print(response)
            message = input("-> ")

# import test_server
from models import ( 
        MissionFactory, MissionLibrary,  DroneStatusStore,
        DroneDispatcher, SlowMission, FastMission, VerboseFastMission)
from simulator import DroneSimulator, DroneMonitor
import unittest
import socket
import time
import mission_data


class DroneDispatcherTests(unittest.TestCase):
    def setUp(self):
        self.host = "127.0.0.1"
        self.drone_port = 8891
        mission_factory = MissionFactory()
        self.missions = mission_factory.create_missions(mission_data)
        self.dispatcher = DroneDispatcher(self.host, self.drone_port)

    def test_get_set_info(self):
        new_host = 8888
        new_port = "192.168.10.1"
        host = self.dispatcher.get_host()
        port = self.dispatcher.get_port()
        self.assertEqual(host, self.host)
        self.assertEqual(port, self.drone_port)
        self.dispatcher.set_port(new_port)
        self.dispatcher.set_host(new_host)
        host = self.dispatcher.get_host()
        port = self.dispatcher.get_port()
        self.assertEqual(host, new_host)
        self.assertEqual(port, new_port)

    def test_send_drone_on_mission(self):
        self.drone_simulator = DroneSimulator()
        self.drone_simulator.start_listening()
        response = self.dispatcher.send_drone_on_mission(self.missions["1"])
        self.assertEqual(response, "you flew mission 1")
        print("waiting for drone simulator to time out")
        for i in range(15,0, -1):
            print(i)
            time.sleep(1)
        self.drone_simulator.stop_reporting()
        self.drone_simulator.stop_listening()
        self.drone_simulator.close_socket()

    def tearDown(self):
        self.dispatcher.close_socket()


class MissionsTests(unittest.TestCase):
    def setUp(self):
        mission_factory = MissionFactory()
        self.missions = mission_factory.create_missions(mission_data)

        def dummy_send_command(message):
            return message

        self.send_command = lambda message: dummy_send_command(message)

    def test_fast_mission(self):
        response = self.missions["1"].execute(self.send_command)

    def test_slow_mission(self):
        response = self.missions["2"].execute(self.send_command)

    def test_verbose_fast_mission(self):
        response = self.missions["3"].execute(self.send_command)


class MissionFactoryTests(unittest.TestCase):

    def test_create_missions_from_py(self):
        mission_factory = MissionFactory()
        missions = mission_factory.create_missions(mission_data)
        index = 0
        for mission_name, mission in missions.items():
            self.assertEqual(mission_name, mission_data.data[index]['name'])
            if isinstance(mission, SlowMission):
                mission_type = 'slow'
            elif isinstance(mission, FastMission):
                mission_type = 'fast'
            elif isinstance(mission, VerboseFastMission):
                mission_type = 'verbosefast'
            self.assertEqual(mission_type, mission_data.data[index]['type'])
            index += 1

    def test_create_missions_from_json(self):
        import json
        f = open("mission_data.json", 'r')
        json_data = json.load(f)
        mission_factory = MissionFactory()
        missions = mission_factory.create_missions_from_file("mission_data.json")
        index = 0
        for mission_name, mission in missions.items():
            self.assertEqual(mission_name, json_data['data'][index]['name'])
            if isinstance(mission, SlowMission):
                mission_type = 'slow'
            elif isinstance(mission, FastMission):
                mission_type = 'fast'
            elif isinstance(mission, VerboseFastMission):
                mission_type = 'verbosefast'
            self.assertEqual(mission_type, json_data['data'][index]['type'])
            index += 1

    def test_create_missions_from_csv(self):
        import csv
        rows = []
        with open("mission_data.csv", "r") as csvfile:
            mission_data_reader = csv.reader(csvfile, delimiter=",")
            for row in mission_data_reader:
                rows.append(row)
        rows.pop(0)
        mission_factory = MissionFactory()
        missions = mission_factory.create_missions_from_file("mission_data.csv")
        index = 0
        for mission_name, mission in missions.items():
            self.assertEqual(mission_name, rows[index][0])
            if isinstance(mission, SlowMission):
                mission_type = 'slow'
            elif isinstance(mission, FastMission):
                mission_type = 'fast'
            elif isinstance(mission, VerboseFastMission):
                mission_type = 'verbosefast'
            self.assertEqual(mission_type, rows[index][2])
            index += 1


class MissionFlyerTests(unittest.TestCase):
    def test_fly_mission(self):
        print("stuff")


class MissionLibraryTests(unittest.TestCase):
    def setUp(self):
        mission_factory = MissionFactory()
        self.missions = mission_factory.create_missions(mission_data)
        self.library = MissionLibrary(self.missions)

    def test_get_mission_names(self):
        mission_names = self.library.get_mission_names()
        self.assertEqual(mission_names, list(self.missions.keys()))

    def test_get_missions(self):
        name = "1"
        mission = self.library.get_mission(name)
        self.assertEqual(mission, self.missions[name])

    def test_add_new_missions(self):
        mission_factory = MissionFactory()
        more_missions = mission_factory.create_missions(mission_data)
        self.library.add_missions(more_missions)


class DroneStatusStoreTests(unittest.TestCase):
    def setUp(self):
        self.initial_status = "pitch:0;roll:0;yaw:0;vgx:0;vgy:0;vgz:0;templ:0;temph:0;tof:0;h:0;bat:100;baro:0.00;time:0;agx:0.00;agy:0.00;agz:0.00;\r\n"
        self.initial_status_dict = {
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
        self.status_store = DroneStatusStore()

    def test_get_latest_status(self):
        latest_status = self.status_store.get_latest_status()
        self.assertEqual(latest_status, self.initial_status)

    def test_update_status(self):
        new_status = "pitch:0;roll:0;yaw:0;vgx:0;vgy:0;vgz:0;templ:0;temph:0;tof:0;h:0;bat:100;baro:1.00;time:3;agx:0.00;agy:0.00;agz:0.00;\r\n"
        self.status_store.update_latest_status(new_status)
        latest_status = self.status_store.get_latest_status()
        self.assertEqual(new_status, latest_status)

    def test_get_status_dict(self):
        status_dict = self.status_store.get_latest_status_dict()
        self.assertEqual(status_dict, self.initial_status_dict)

    def test_update_status_with_dict(self):
        status_dict = self.status_store.get_latest_status_dict()
        status_dict["h"] = 100
        self.status_store.update_latest_status_with_dict(status_dict)
        latest_status_dict = self.status_store.get_latest_status_dict()
        self.assertEqual(latest_status_dict, status_dict)

class DroneMonitorTests(unittest.TestCase):

    def test_listen_for_status(self):
        self.host = "127.0.0.1"
        self.drone_port = 8891
        mission_factory = MissionFactory()
        self.missions = mission_factory.create_missions(mission_data)
        self.drone_simulator = DroneSimulator()
        self.drone_simulator.start_listening()
        self.drone_monitor = DroneMonitor()
        self.dispatcher = DroneDispatcher(self.host, self.drone_port)
        response = self.dispatcher.send_drone_on_mission(self.missions["1"])
        self.drone_simulator.stop_reporting()
        self.drone_simulator.stop_listening()
        self.drone_monitor.stop_listening()
        latest_status_dict = self.drone_monitor.status_store.get_latest_status_dict()
        self.assertNotEqual(0, latest_status_dict['time'])
        self.dispatcher.close_socket()
        self.drone_monitor.close_socket()
        self.drone_simulator.close_socket()

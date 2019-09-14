# import test_server
from models import DroneDispatcher
from models import ClientCli
from models import MissionFactory
import unittest
import socket
import time
import mission_data


class test_drone_dispatcher(unittest.TestCase):

    def setUp(self):
        self.host = "127.0.0.1"
        self.drone_port = 8889
        mission_factory = MissionFactory()
        missions = mission_factory.create_missions(mission_data)
        self.dispatcher = DroneDispatcher(missions, self.host, self.drone_port)

    def tearDown(self):
        self.dispatcher.close_socket()

    def test_get_mission_names(self):
        mission_names = self.dispatcher.get_mission_names()
        self.assertEqual(mission_names, ["1", "2", "3"])

    def test_get_set_info(self):
        new_host = 8888
        new_port = "192.168.10.1"
        host, port = self.dispatcher.get_info()
        self.assertEqual(host, self.host)
        self.assertEqual(port, self.drone_port)
        self.dispatcher.set_port(new_port)
        self.dispatcher.set_host(new_host)
        host, port = self.dispatcher.get_info()
        self.assertEqual(host, new_host)
        self.assertEqual(port, new_port)

    def test_mission_one(self):
        response = self.dispatcher.fly_mission("1")
        self.assertEqual(response, "you flew mission 1")

    def test_mission_two(self):
        response = self.dispatcher.fly_mission("2")
        self.assertEqual(response, "you flew mission 2")

    def test_mission_three(self):
        response = self.dispatcher.fly_mission("3")
        self.assertEqual(response, "you flew mission 3")


class test_missions(unittest.TestCase):

    def setUp(self):
        mission_factory = MissionFactory()
        self.missions = mission_factory.create_missions(mission_data)

    def test_mission(self):
        print("stuff")

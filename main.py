from models import DroneDispatcher
from models import MissionFactory
from models import Menu
import mission_data


def Main():
    mission_factory = MissionFactory()
    missions = mission_factory.create_missions(mission_data)
    dispatcher = DroneDispatcher(missions)
    menu_methods = {
                'ls': dispatcher.get_mission_names,
                'load': mission_factory.create_missions_from_file,
                'set port': dispatcher.set_port,
                'set host': dispatcher.set_host,
                'get port': dispatcher.get_port,
                'get host': dispatcher.get_host,
            }
    menu = Menu(menu_methods)
    menu.display_menu()


if __name__ == "__main__":
    Main()

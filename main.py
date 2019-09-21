from models import DroneDispatcher MissionFactory MissionLibrary MissionFactory Menu
import mission_data


def Main():
    mission_factory = MissionFactory()
    missions = mission_factory.create_missions(mission_data)
    dispatcher = DroneDispatcher()
    library = MissionLibrary(missions)
    menu_methods = {
                'ls': dispatcher.get_mission_names,
                'load': mission_factory.create_missions_from_file,
                'set port': dispatcher.set_port,
                'set host': dispatcher.set_host,
                'get port': dispatcher.get_port,
                'get host': dispatcher.get_host,
                'get mission': lambda name: library.get_mission(name),
                'mission': dispatcher.send_drone_on_mission,
            }
    menu = Menu(menu_methods)
    menu.display_menu()


if __name__ == "__main__":
    Main()

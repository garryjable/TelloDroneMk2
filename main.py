from models import DroneDispatcher
from models import ClientCli


def Main():
    cli = ClientCli()
    cli.start_client()


if __name__ == "__main__":
    Main()

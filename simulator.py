import socket


host = "127.0.0.1"
port = 8889

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))


    drone_monitor.update_position(params[1])
    return "ok"

drone_status = {
        

        }


commands = {
        "command": lambda params: handleCommand(params),
        "takeoff": lambda params: handleTakeoff(params),
        "land": lambda params: handleLand(params),
        "up": lambda params: handleUp(params),
        "right": lambda params: handleRight(params),
        "down": lambda params: handleDown(params),
        "left": lambda params: handleLeft(params),
}

print("Server Started")
while True:
    data, addr = s.recvfrom(1024)
    print("message from: " + str(addr))
    print("from connect user: " + str(data.decode()))
    data = str(data.decode()))
    args = data.split(' ')
    try:
        response = commands[args[0]](args)
    except:
        response = "error" 
    print("sending: " + str(response))
    s.sendto(data.encode(), addr)
s.close()

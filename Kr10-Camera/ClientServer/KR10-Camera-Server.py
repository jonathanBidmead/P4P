import opcua
from time import sleep
from random import randint
from datetime import datetime


url = "localhost"
port = 5001
endpoint = "opc.tcp://{}:{}".format(url,port)

myserver = opcua.Server()
myserver.set_endpoint(endpoint)

name = "KR10 Camera"

addspace = myserver.register_namespace(name)
objects = myserver.get_objects_node()
param = objects.add_object(addspace,"parameters")

x_coordinate = param.add_variable(addspace,"x_coordinate","NA")



try:

    # starting! The server will continue running
    myserver.start()
    current_time = str(datetime.now().time())[:-7]
    print("{} - Server is initialising...".format(current_time))

    clock = opcua.Client("opc.tcp://localhost:4840")
    clock.connect()
    print("Clock is connected....")

    while True:
        cl = clock.get_node("ns=2;i=2")
        old = cl.get_value()
        sleep(0.3)
        new = cl.get_value()

        if old == False and new == True:
            current_time = str(datetime.now().time())[:-7]
            current_temp = randint(10, 25)

            x_coordinate.set_value(current_temp)  # publish temperature value
            print("{} - X : {} ".format(current_time, current_temp))
            sleep(1)

finally:
    myserver.stop()
    clock.disconnect()



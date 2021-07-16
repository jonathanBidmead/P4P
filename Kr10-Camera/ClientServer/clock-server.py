import opcua
from time import sleep
from random import randint
from datetime import datetime


url = "localhost"
port = 4840
endpoint = "opc.tcp://{}:{}".format(url,port)

myserver = opcua.Server()
myserver.set_endpoint(endpoint)

name = "Clock"

addspace = myserver.register_namespace(name)
objects = myserver.get_objects_node()
param = objects.add_object(addspace,"parameters")

timer = param.add_variable(addspace,"timer","NA")



try:

    # starting! The server will continue running
    myserver.start()
    current_time = str(datetime.now().time())[:-7]
    print("{} - Server is initialising...".format(current_time))

    while True:
        timer.set_value(False)
        print("Time : {} ".format(timer.get_value()))
        sleep(5)
        current_time = str(datetime.now().time())[:-7]

        timer.set_value(True)  # publish temperature value
        print("Time : {} ".format(timer.get_value()))
        sleep(1)
        

finally:
    myserver.stop()



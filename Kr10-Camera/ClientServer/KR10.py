from time import sleep
from random import randint
from datetime import datetime
import opcua


#Server
url = "localhost"
port = 7001
endpoint = "opc.tcp://{}:{}".format(url,port)

myserver = opcua.Server()
myserver.set_endpoint(endpoint)

name = "KR10"

addspace = myserver.register_namespace(name)
objects = myserver.get_objects_node()
param = objects.add_object(addspace,"parameters")

motor = param.add_variable(addspace,"motor","NA")

###################################################################3

#Client
client = opcua.Client("opc.tcp://localhost:5001")

clock = opcua.Client("opc.tcp://localhost:4840")


try:
    #Server Starting
    myserver.start()
    current_time = str(datetime.now().time())[:-7]
    print("{} - Server is initialising...".format(current_time))

    #Client
    client.connect()
    current_time = str(datetime.now().time())[:-7]
    print("{} - Client is Connecting...".format(current_time))

    current_motor = True

    clock.connect()


    while True:
        cl = clock.get_node("ns=2;i=2")
        old = cl.get_value()
        sleep(0.3)
        new = cl.get_value()
        if old == False and new == True:
            if(current_motor): current_motor = False
            else: current_motor = True
            motor.set_value(current_motor)  # publish temperature value
            print("{} - Motor : {} ".format(current_time, current_motor))



            x = client.get_node("ns=2;i=2")
            print(x.get_value())
            sleep(1)

except Exception as e:
    print(e)

finally:
    myserver.stop()
    client.disconnect()
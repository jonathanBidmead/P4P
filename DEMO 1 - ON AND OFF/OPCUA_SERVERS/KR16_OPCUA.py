import opcua
from opcua import uamethod
from datetime import datetime
import sys, os
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
import time



#server params
url = "localhost"
port = 7004#CHANGE
end_point = "opc.tcp://{}:{}".format(url, port)
name = "KR16_SERVER"
# create server instance/object
movementServer = smartServer.smartOpcua(url,port,name,'server')

# # Assign endpoint url on the OPC UA server address space
# movementServer.server.set_endpoint(end_point)

# # Create a name for OPC UA namespace
# name = "movement server"

# # Register the name on OPC UA namespace
# addSpace = movementServer.server.register_namespace(name)

# # Get reference to the Objects node of the OPC UA server
# objects = movementServer.server.get_objects_node()

# # Create objects on the object node
# param = objects.add_object(addSpace, "parameters")

#internal flags
move_start_flag = False
#TODO: KVP server on which this is based uses a lot of buffers for stuff, does this need em too?
startPoint_internal = ""
endPoint_internal = ""

movementServer.objects.add_variable(movementServer.addspace,"busy",False)

@uamethod
def beginMove(parent,startPoint,endPoint):
    global move_start_flag
    global startPoint_internal
    global endPoint_internal
    move_start_flag = True
    startPoint_internal = startPoint
    endPoint_internal = endPoint
    print("beginning new motion")
    movementServer.objects.get_children()[2].set_value(True)
    return "Beginning movement from {} to {}".format(startPoint,endPoint)


def move(startPoint,endPoint):
    print("Beginning movement from {} to {}".format(startPoint,endPoint))
    time.sleep(1)
    global move_start_flag
    move_start_flag = False
    print("Movement Complete")
    movementServer.objects.get_children()[2].set_value(False)

#add methods to opcua server
movementServer.addMethods([beginMove],["beginMove"])


# starting! The server will continue running
try:
    current_time = str(datetime.now().time())[:-7]
    print("{} - OPC UA server has been successfully initialised...".format(current_time))
    print("{} - Connect to OPC UA server via \"{}\"...".format(current_time, end_point))
    movementServer.server.start()
except:
    print("!!!ERROR!!! Failure to initialise the OPC UA server...")
    sys.exit()

while True:

    if(move_start_flag == True):
        print("move flag true")
        move(startPoint_internal,endPoint_internal)


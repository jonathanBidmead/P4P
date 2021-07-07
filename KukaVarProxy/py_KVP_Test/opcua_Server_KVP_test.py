import opcua
from opcua import uamethod
from random import randint
from time import sleep
from datetime import datetime
import sys
from py_openshowvar import openshowvar

# create instance/object of type opcua.Server
KVP_Server = opcua.Server()
KVP_client = openshowvar('10.104.117.1',7000)
url = "localhost"
port = 7001
end_point = "opc.tcp://{}:{}".format(url, port)

# Assign endpoint url on the OPC UA server address space
KVP_Server.set_endpoint(end_point)

# Create a name for OPC UA namespace
name = "KVP Control"

# Register the name on OPC UA namespace
addSpace = KVP_Server.register_namespace(name)

# Get reference to the Objects node of the OPC UA server
objects = KVP_Server.get_objects_node()

# Create objects on the object node
param = objects.add_object(addSpace, "parameters")

global_X = param.add_variable(addSpace,"Global Coordinates",0)
global_Y = param.add_variable(addSpace,"Global Coordinates",0)
global_Z = param.add_variable(addSpace,"Global Coordinates",0)
global_A = param.add_variable(addSpace,"Global Coordinates",0)
global_B = param.add_variable(addSpace,"Global Coordinates",0)
global_C = param.add_variable(addSpace,"Global Coordinates",0)

global_X.set_writable()

@uamethod
def getCurrentPosition(parent):
    pos_string = KVP_client.read('$POS_ACT', debug=False)
    pos_string = pos_string.decode("utf-8")
    pos_string = pos_string.replace(',','')
    pos = pos_string.split()

    print(pos[2])
    print(pos[4])
    print(pos[6])
    print(pos[8])
    print(pos[10])
    print(pos[12])
    return([float(pos[2]),float(pos[4]),float(pos[6]),float(pos[8]),float(pos[10]),float(pos[12])])

objects.add_method(1, "getPos", getCurrentPosition)

# starting! The server will continue running
try:
    current_time = str(datetime.now().time())[:-7]
    print("{} - OPC UA server has been successfully initialised...".format(current_time))
    print("{} - Connect to OPC UA server via \"{}\"...".format(current_time, end_point))
    KVP_Server.start()
except:
    print("!!!ERROR!!! Failure to initialise the OPC UA server...")
    sys.exit()
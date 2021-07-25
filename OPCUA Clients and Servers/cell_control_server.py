import opcua
from opcua import uamethod
from random import randint
from time import sleep
from datetime import datetime
import sys

# create instance/object of type opcua.Server
Cell_Server = opcua.Server()

url = "localhost"
port = 7001
end_point = "opc.tcp://{}:{}".format(url, port)

# Assign endpoint url on the OPC UA server address space
Cell_Server.set_endpoint(end_point)

# Create a name for OPC UA namespace
name = "Cell Control"

# Register the name on OPC UA namespace
addSpace = Cell_Server.register_namespace(name)

# Get reference to the Objects node of the OPC UA server
objects = Cell_Server.get_objects_node()

# Create objects on the object node
param = objects.add_object(addSpace, "parameters")


#Internal Variables
IRID_list = ["KR10","KR16_circ","KR16_lin"]
IR_pin_list = [3,8,6]

output_list = ["KR10_grip", "KR16_grip", "circ_conveyor_onoff", "circ_conveyor_piston"]
output_pin_list = [6,5,1,4]

#Methods to define:
#IR[n] status
#OUT[1-6] ON/OFF

#test external variable
testParam = param.add_variable(addSpace, "Test Type", 2)
testParam.set_writable()
@uamethod
def getIRstatus(parent,IRID):
    pin = IR_pin_list[IRID_list.index(IRID)]
    #read (pin) value
    pass

@uamethod
def setPin(pinID, value):
    pin = output_pin_list[output_list.index(pinID)]
    #sets output pin (pinID) to (value), either HIGH or LOW
    pass

@uamethod
def getIRPinAssignments(parent):
    return IRID_list

@uamethod
def getOutputPinAssignments(parent):
    return output_pin_list

objects.add_method(addSpace, "getIRstatus", getIRstatus)
objects.add_method(addSpace, "setPin", setPin)
objects.add_method(addSpace, "getIRAssignments", getIRPinAssignments)
objects.add_method(addSpace, "getOutputAssignments", getOutputPinAssignments)

try:
    current_time = str(datetime.now().time())[:-7]
    print("{} - OPC UA server has been successfully initialised...".format(current_time))
    print("{} - Connect to OPC UA server via \"{}\"...".format(current_time, end_point))
    Cell_Server.start()
except:
    print("!!!ERROR!!! Failure to initialise the OPC UA server...")
    sys.exit()

# print(objects.get_browse_name())
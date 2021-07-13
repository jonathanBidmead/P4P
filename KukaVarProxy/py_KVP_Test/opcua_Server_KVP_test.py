import opcua
from opcua import uamethod
from random import randint
from time import sleep
from datetime import datetime
import sys
from py_openshowvar import openshowvar
from math import sqrt

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

def getCurrentPos_Internal():
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

def sqrt_of_squares(input):
    sumInternal = 0
    for i in input:
        sumInternal += i*i
    return sqrt(sumInternal)


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

@uamethod
def moveDirectKR10(parent, point):
    print("Attempting to move KR10")
    initialPos = getCurrentPos_Internal()
    print("initialPos")
    print(initialPos)
    
    
    point_rel = [0,0,0,0,0,0]
    for p in range(6):
        point_rel[p] = point[p] - initialPos[p]
    print("relative movement")
    print(point_rel) 
    pos_asString = "{{X {}, Y {}, Z {}, A {}, B {}, C {}}}".format(point_rel[0], point_rel[1], point_rel[2], point_rel[3], point_rel[4], point_rel[5])
    print(pos_asString)
    if (KVP_client.read('my_step').decode('utf-8') == 'FALSE'):
        debug_rite_var = KVP_client.write('my_inc',pos_asString,debug=False)
        debug_write_var = KVP_client.write('my_step','TRUE',debug=False)
    
#Not working properly atm. The idea is that this keeps sending the same point to the robot until it actually reaches the point, but there 
#must be some mathematical error somewhere because I think the point it's telling the robot to go to keeps changing (badly)
@uamethod
def moveDirectKR16(parent, point):
    epsilon = 0.1
    initialPos = getCurrentPos_Internal()
    point_check = sqrt_of_squares(point)
    newPos_check = point_check + epsilon + 10 #arbitrary value added so the loop can start
    
    while abs(newPos_check - point_check) > epsilon:#TODO: This condition kinda sucks, edge case where multiple XYZABCs result in same sqrt sum
        print("Point Check", point_check)
        print("new pos check", newPos_check)
        initialPos = getCurrentPos_Internal()

        
        point_rel = [0,0,0,0,0,0]

        for p in range(6):
            point_rel[p] = point[p] - initialPos[p]
        print("Function Called")
        
        if (KVP_client.read('my_step').decode('utf-8') == 'FALSE'):
            newPos = getCurrentPos_Internal()
            newPos_check = sqrt_of_squares(newPos)

            debug_write_var = KVP_client.write('MYX',str(point_rel[0]),debug=False)
            debug_write_var = KVP_client.write('MYY',str(point_rel[1]),debug=False)
            debug_write_var = KVP_client.write('MYZ',str(point_rel[2]),debug=False)
            debug_write_var = KVP_client.write('MYA',str(point_rel[3]),debug=False)
            debug_write_var = KVP_client.write('MYB',str(point_rel[4]),debug=False)
            debug_write_var = KVP_client.write('MYC',str(point_rel[5]),debug=False)
            debug_write_var = KVP_client.write('MYE1',str(0),debug=False)#TODO: Implement E1 Properly
            KVP_client.write('my_step','TRUE')
            print("Point Sent to Robot")
        sleep(1)
        print("Looped")



@uamethod
def moveDirectKR16_relative(parent, point):
    point_rel = point
    print("Function Called")
    if (KVP_client.read('my_step').decode('utf-8') == 'FALSE'):
        debug_write_var = KVP_client.write('MYX',str(point_rel[0]),debug=False)
        debug_write_var = KVP_client.write('MYY',str(point_rel[1]),debug=False)
        debug_write_var = KVP_client.write('MYZ',str(point_rel[2]),debug=False)
        debug_write_var = KVP_client.write('MYA',str(point_rel[3]),debug=False)
        debug_write_var = KVP_client.write('MYB',str(point_rel[4]),debug=False)
        debug_write_var = KVP_client.write('MYC',str(point_rel[5]),debug=False)
        debug_write_var = KVP_client.write('MYE1',str(0),debug=False)#TODO: Implement E1 Properly
        KVP_client.write('my_step','TRUE')
        print("Point Sent to Robot")

objects.add_method(1, "moveKR10", moveDirectKR10)
objects.add_method(1, "moveKR16", moveDirectKR16)
objects.add_method(1, "moveKR16_rel", moveDirectKR16_relative)
# starting! The server will continue running
try:
    current_time = str(datetime.now().time())[:-7]
    print("{} - OPC UA server has been successfully initialised...".format(current_time))
    print("{} - Connect to OPC UA server via \"{}\"...".format(current_time, end_point))
    KVP_Server.start()
except:
    print("!!!ERROR!!! Failure to initialise the OPC UA server...")
    sys.exit()
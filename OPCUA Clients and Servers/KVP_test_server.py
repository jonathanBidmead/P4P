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

# create instances of KVP Servers
KVP_client = openshowvar('10.104.117.1',7000)
# Deprecated attempt to make the server generic (not necessary, better to have seperate servers)
# KR16_client = openshowvar('10.104.117.2',7000)
# KVP_clients = {}
# KVP_clients[0] = KR10_client
# KVP_clients[1] = KR16_client

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

#defining flags for internal server use
rel_start_flag = False
abs_start_flag = False
premade_start_flag = False
# system_is_busy = False

#buffer for point movement
buffer = []
buffer_type = []

#list of premade points/paths defined within KRL code
premade_points_list = ["CV_HOME", "DEPOSIT_IN_LATHE", "REMOVE_FROM_LATHE", "GLOBAL_HOME"]
target_premade_point = ""

#Returns the current position as read from the robot 
#Note: If "Tool" and "Base" are not set in the HMI/Teachpad, this method will fail and there is no error handling as yet,
def getCurrentPos_Internal():
    print("Inevitable Print from KVP Read")#openshowvar's .read() method always prints to the console, and I don't know of a way to disable it.
    #.read() returns a string of format something like "{E6POS: X 100, Y 200 ... }", these lines extract the relevant numbers
    
    pos_string = KVP_client.read('$POS_ACT', debug=False)
    pos_string = pos_string.decode("utf-8")
    pos_string = pos_string.replace(',','')
    pos = pos_string.split()

    print("Current Pos From KVP")
    print(pos[2])
    print(pos[4])
    print(pos[6])
    print(pos[8])
    print(pos[10])
    print(pos[12])
    return([float(pos[2]),float(pos[4]),float(pos[6]),float(pos[8]),float(pos[10]),float(pos[12])])

#This function is used to define the exit condition of the loops inside the movement methods. It just computes sqrt(a^2 + b^2 + ...), but this could be any arbitrary function
def sqrt_of_squares(input):
    sumInternal = 0
    for i in input:
        sumInternal += i*i
    return sqrt(sumInternal)

#@uamethod means the function is accessible via OPCUA 
#This method is identical to getCurrentPosition_Internal, except it can be accessed via OPCUA (and cannot be accessed internally, as far as I can tell - hence the seperate functions)
@uamethod
def getCurrentPosition(parent):#"parent" argument is required of all OPCUA methods, but I have no idea why or what it does
    
    pos_string = KVP_client.read('$POS_ACT', debug=False)
    pos_string = pos_string.decode("utf-8")
    pos_string = pos_string.replace(',','')
    pos = pos_string.split()

    # print(pos[2])
    # print(pos[4])
    # print(pos[6])
    # print(pos[8])
    # print(pos[10])
    # print(pos[12])
    return([float(pos[2]),float(pos[4]),float(pos[6]),float(pos[8]),float(pos[10]),float(pos[12])])

#adding the method to the OPCUA addressSpace or methodSpace or whatever the jargon is - you need to do this to be able to access it from a client
objects.add_method(1, "getPos", getCurrentPosition)


# internal method that does the actual moving of the KR10
def moveDirect_absolute(point):
    epsilon = 0.1
    i = 1
    initialPos = getCurrentPos_Internal()
    point_check = sqrt_of_squares(point)
    newPos_check = point_check + epsilon + 10 #arbitrary value added so the loop can start
    
    #while current pos != desired pos
    while abs(newPos_check - point_check) > epsilon:#TODO: This condition kinda sucks, edge case where multiple XYZABCs result in same sqrt sum
        print("Point Check", point_check)
        print("new pos check", newPos_check)
        #get new initialPos to re-calculate relative position of point
        initialPos = getCurrentPos_Internal()

        
        point_rel = [0,0,0,0,0,0]

        #get difference, TODO: implement something to do with angles and +/-360 degrees?
        for p in range(3):
            point_rel[p] = point[p] - initialPos[p]
        
        for p in range(3):
            diff = point[p+3] - initialPos[p+3]
            if (abs(diff) > 180):
                point_rel[p+3] = -(360-diff)
            else:
                point_rel[p+3] = diff

        #functionally the same as initialPos now, but kept seperate for clarity/because I'm lazy idk
        newPos = getCurrentPos_Internal()
        newPos_check = sqrt_of_squares(newPos)
        print("Updated New Pos Check", newPos_check)
        # newPos_check = 1

        #only send a new point to the robot if it has finished the previous motion
        if (KVP_client.read('my_step').decode('utf-8') == 'FALSE'):
            

            KVP_client.write('MYX',str(point_rel[0]))
            KVP_client.write('MYY',str(point_rel[1]))
            KVP_client.write('MYZ',str(point_rel[2]))
            KVP_client.write('MYA',str(point_rel[3]))
            KVP_client.write('MYB',str(point_rel[4]))
            KVP_client.write('MYC',str(point_rel[5]))
            KVP_client.write('MYE1',str(0))#TODO: Implement E1 Properly
            KVP_client.write('my_step','TRUE')
            print("Point Sent to Robot")
        sleep(1)
        print("Looped {} time(s)".format(i))
        i+=1

    #set flag to false so this method isn't called again unduly
    global abs_start_flag 
    abs_start_flag = False

# TODO: make this do the continuous re-checking like it does for absolute
def moveDirect_relative(point):
    point_rel = point
    print("Function Called")
    if (KVP_client.read('my_step').decode('utf-8') == 'FALSE'):
        KVP_client.write('MYX',str(point_rel[0]))
        KVP_client.write('MYY',str(point_rel[1]))
        KVP_client.write('MYZ',str(point_rel[2]))
        KVP_client.write('MYA',str(point_rel[3]))
        KVP_client.write('MYB',str(point_rel[4]))
        KVP_client.write('MYC',str(point_rel[5]))
        KVP_client.write('MYE1',str(0))#TODO: Implement E1 Properly
        KVP_client.write('my_step','TRUE')
        print("Point Sent to Robot")
        #Movement Complete so set flag accordingly
        global rel_start_flag 
        rel_start_flag = False

def moveDirect_premade(point):
    global premade_start_flag
    KVP_client.write(point,'TRUE')
    premade_start_flag = False


@uamethod
def beginMove_absolute(parent, point):
    global abs_start_flag
    global target_point
    target_point = point
    #store point in buffer, don't move yet
    global buffer
    buffer.append(point)
    buffer_type.append(0)
    abs_start_flag = True
    return "Absolute Point Sent"

@uamethod
def beginMove_relative(parent, point):
    # global rel_start_flag
    global target_point
    target_point = point
    global buffer
    buffer.append(point)
    buffer_type.append(1)
    # rel_start_flag = True
    return "Relative Point {} Sent".format(point)

@uamethod
def beginMove_predefined(parent, point):
    global target_premade_point
    global premade_start_flag
    target_premade_point = point
    premade_start_flag = True
    return "Predefined Point {} Sent".format(point)


objects.add_method(1, "beginMove_abs", beginMove_absolute)
objects.add_method(1, "beginMove_rel", beginMove_relative)
objects.add_method(1, "beginMove_premade", beginMove_predefined)
# starting! The server will continue running
try:
    current_time = str(datetime.now().time())[:-7]
    print("{} - OPC UA server has been successfully initialised...".format(current_time))
    print("{} - Connect to OPC UA server via \"{}\"...".format(current_time, end_point))
    KVP_Server.start()
except:
    print("!!!ERROR!!! Failure to initialise the OPC UA server...")
    sys.exit()

#Continuously checking for new points being sent to the system
while True:
    if (rel_start_flag):
        print("Beginning Relative Motion")
        buffer.pop(0)
        buffer_type.pop(0)
        moveDirect_relative(target_point)
        
    if (abs_start_flag):
        print("Beginning Absolute Motion")
        buffer.pop(0)
        buffer_type.pop(0)
        moveDirect_absolute(target_point)

    if (premade_start_flag):
        print('Beginning Premade Motion')
        moveDirect_premade(target_premade_point)
    
    else:
        if (len(buffer) > 0):
            target_point = buffer[0]
            if (buffer_type[0] == 0):
                abs_start_flag = True
                rel_start_flag = False
            if (buffer_type[0] == 1):
                rel_start_flag = True
                abs_start_flag = False
            
import opcua
import linPart
from time import sleep
from opcua import Client
url = "192.168.137.39"
port = 7003
end_point = "opc.tcp://{}:{}".format(url, port)
opcClient = Client(end_point)
opcClient.connect()
print("Client Did Something")
# Get the root node of the adress space
objects_node = opcClient.get_objects_node()

# Get the children node of the objects Method
method = objects_node.get_children()

# global_X_test = opcClient.get_node("ns=2;i=1")
print(method)

getCurrentPosition = method[2]
startMove_abs = method[3]
startMove_rel = method[4]
startMove_premade = method[5]
is_robot_busy = method[6]



url1 = "192.168.137.139"
port1 = 7004
end_point1 = "opc.tcp://{}:{}".format(url1, port1)
opcClient1 = Client(end_point1)
opcClient1.connect()
print("Client1 Did Something")


x = 0
y = 0
z = 0
pointA = [900,100,1114,180,0,-180]
pointB = [-66.8,-593.2,1252.8,90,0,180]
pointC = [-85.2+x,-583.7+y,1124.3+z,1,-0.5,178.4]
pointD = [0,0,120,0,0,0]
pointE = [-200,-200,0,0,0,0]

y_part,x_part = linPart.findPart()
pointPart = [-x_part,-y_part,0,0,0,0]
# objects_node.call_method(startMoveKR10_abs,pointB,"KR10")
# sleep(50)
objects_node.call_method(startMove_premade,"CV_HOME")
objects_node.call_method(startMove_rel,pointPart)

pointDown = [0,0,-35,0,0,0,0]
objects_node.call_method(startMove_rel,pointDown)

sleep(15)
while objects_node.call_method(is_robot_busy):
    pass

objects_node1 = opcClient1.get_objects_node()

methods = objects_node1.get_children()

gripperOn = methods[2]
gripperOff = methods[3]

objects_node1.call_method(gripperOn)


# sleep(30)
# objects_node.call_method(startMoveKR10_rel,pointE)

# test = objects_node.call_method(getCurrentPosition,"KR10")
# print(test)

sleep(5)

opcClient.disconnect()
opcClient1.disconnect()

exit()
from time import sleep
from opcua import Client
url = "localhost"
port = 7003
end_point = "opc.tcp://{}:{}".format(url, port)
opcClient = Client(end_point)
opcClient.connect()

# url2 = 
# port2 = 
# end_point2 = "opc.tcp://{}:{}".format(url, port)
# CV_client = Client(end_point2)

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
x = 0
y = 0
z = 0
pointA = [-70,-586,1278,90,0,180]
pointB = [-70,44,-63,198,-90,198]
pointC = [-70,-586,1278,-108,90,-108]
pointD = [0,0,60,0,0,0]
pointE = [-200,-200,0,0,0,0]
# print(objects_node.call_method(startMove_abs,pointA))
print(objects_node.call_method(startMove_premade, "CV_HOME"))
print(objects_node.call_method(startMove_rel, pointE))
print(objects_node.call_method(startMove_rel, pointD))
print(objects_node.call_method(startMove_premade, "DEPOSIT_IN_LATHE"))
print(objects_node.call_method(startMove_premade, "PLATFORM"))
print(objects_node.call_method(startMove_rel, pointD))
print(objects_node.call_method(startMove_premade, "GLOBAL_HOME"))
# print(objects_node.call_method(startMove_rel,pointE))
# print(objects_node.call_method(startMove_rel,pointD))


# def goto_part():
#     print(objects_node.call_method(startMove_premade, "CV_HOME"))
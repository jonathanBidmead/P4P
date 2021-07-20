from time import sleep
from opcua import Client
url = "localhost"
port = 7001
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
startMoveKR10_abs = method[3]
startMoveKR10_rel = method[4]

x = 0
y = 0
z = 0
pointA = [900,100,1114,180,0,-180]
pointB = [-85.2,-583.7,1124.3,1,-0.5,178.4]
pointC = [-85.2+x,-583.7+y,1124.3+z,1,-0.5,178.4]
pointD = [0,0,120,0,0,0]
pointE = [-200,-200,0,0,0,0]
# objects_node.call_method(startMoveKR10_abs,pointC,"KR10")
# sleep(50)
# objects_node.call_method(startMoveKR10_rel,pointD)
# sleep(30)
# objects_node.call_method(startMoveKR10_rel,pointE)

# test = objects_node.call_method(getCurrentPosition,"KR10")
# print(test)
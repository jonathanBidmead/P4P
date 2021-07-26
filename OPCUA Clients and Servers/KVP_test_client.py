from time import sleep
from opcua import Client
url = "172.23.114.90"
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
pointA = [-70,-586,1278,90,0,180]
pointB = [-70,44,-63,198,-90,198]
pointC = [-70,-586,1278,-108,90,-108]
pointD = [0,0,-60,0,0,0]
pointE = [-200,-200,0,0,0,0]
print(objects_node.call_method(startMoveKR10_abs,pointC,"KR10"))
# print(objects_node.call_method(startMoveKR10_rel,pointB, "KR10"))
# sleep(50)
# objects_node.call_method(startMoveKR10_rel,pointD)
# sleep(30)
# objects_node.call_method(startMoveKR10_rel,pointE)

# test = objects_node.call_method(getCurrentPosition,"KR10")
# print(test)
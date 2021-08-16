from time import sleep
from opcua import Client

url = "localhost"
port = 7005
end_point = "opc.tcp://{}:{}".format(url, port)
opcClient = Client(end_point)
opcClient.connect()

# Get the root node of the adress space
objects_node = opcClient.get_objects_node()

# Get the children node of the objects Method
method = objects_node.get_children()

# global_X_test = opcClient.get_node("ns=2;i=1")
print(method)
start_node = 'Linear Conveyor'
end_node = 'Lathe'
wip_path = objects_node.call_method(method[2],start_node,end_node)
print(wip_path)
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

global_X_test = opcClient.get_node("ns=2;i=1")
print(method)
print(global_X_test.get_properties())
getCurrentPosition = method[2]
getPos = objects_node.call_method(getCurrentPosition)
print(getPos)
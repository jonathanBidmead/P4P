from opcua import Client
url = "localhost"
port = 7001
end_point = "opc.tcp://{}:{}".format(url, port)
opcClient = Client(end_point)
opcClient.connect()
# Get the root node of the adress space
objects_node = opcClient.get_objects_node()

# Get the children node of the objects Method
method = objects_node.get_children()

getCurrentPosition = method[1]

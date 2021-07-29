from opcua import Client

url = "192.168.137.139"
port = 7004
end_point = "opc.tcp://{}:{}".format(url, port)
cell_client = Client(end_point)
cell_client.connect()
print("connected")
# Get the root node of the adress space
objects_node = cell_client.get_objects_node()

# Get the children node of the objects Method
method = objects_node.get_children()

# print(method)

# for node in method:
#     print(node.get_browse_name().to_string())

gripperOn = method[2]
gripperOff = method[3]

objects_node.call_method(gripperOff)

# objects_node.call_method(gripperOff)

from opcua import Client

url = "192.168.137.255"
port = 7001
end_point = "opc.tcp://{}:{}".format(url, port)
cell_client = Client(end_point)
cell_client.connect()

# Get the root node of the adress space
objects_node = cell_client.get_objects_node()

# Get the children node of the objects Method
method = objects_node.get_children()

print(method)

for node in method:
    print(node.get_browse_name().to_string())

print(method[1].get_children()[0].get_value())
print(method[1].get_children()[0].set_value(3))
print(method[1].get_children()[0].get_value())


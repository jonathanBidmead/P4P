from opcua import Client
from time import sleep
import utils

#connect to all servers (generate all clients)
number_of_servers = 1
clients = []
urls = ["localhost","localhost"]
ports = [7001,7002]

for i in range(number_of_servers):
    end_point = "opc.tcp://{}:{}".format(urls[i], ports[i])
    clients.append(Client(end_point))
    clients[i].connect()
    print("looped once")
print("done")

#list all nodes' browsenames from connected servers
objects_nodes = []
methods = []
for i in range(number_of_servers):
    objects_nodes.append(clients[i].get_objects_node())
    methods.append(objects_nodes[i].get_children())
    print(methods[i].get_browse_name())
#

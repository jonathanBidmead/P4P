from time import sleep
from datetime import datetime
import sys
sys.path.append("/C:/Users/drago/OneDrive/Documents/GitHub/P4P/MultiAgent")
from MultiAgent import smartServer
import opcua
from opcua import uamethod
# import opcua
# from opcua import uamethod
# import paho.mqtt.client as mqtt
#TODO: get Sahil's server class in here
url = "localhost"
port = 7005
end_point = "opc.tcp://{}:{}".format(url, port)

GraphServer = smartServer.smartOpcua(url,port,'Graph Server','server')
# GraphServer = opcua.Server()

# # Assign endpoint url on the OPC UA server address space
# GraphServer.set_endpoint(end_point)

# # Create a name for OPC UA namespace
# name = "KVP Control"

# # Register the name on OPC UA namespace
# addSpace = GraphServer.register_namespace(name)

# # Get reference to the Objects node of the OPC UA server
# objects = GraphServer.get_objects_node()


max_iters = 256

start_node = 'Linear Conveyor'
end_node = 'Lathe'

#TODO: Convert to enums maybe to bypass the tyranny of spelling
layout_graph = {
'Linear Conveyor': set(['KR16']),
'KR16': set(['Linear Conveyor', 'Circular Conveyor', 'Platform']),
'Circular Conveyor': set(['KR16', 'KR10']),
'Platform': set(['KR16']),
'KR10': set(['Circular Conveyor', 'Lathe', 'Exit Platform']),
'Lathe': set(['KR10']),
'Exit Platform': set(['KR10'])
}

availability_graph = {
'Linear Conveyor':set(['ON']),
'KR16':set(['ON']),
'Circular Conveyor':set(['ON']),
'Platform':set(['ON']),
'KR10':set(['ON']),
'Lathe':set(['ON']),
'Exit Platform':set(['ON'])
}

@uamethod
def bfs(parent, start, end):
    print(layout_graph)
    initial_graph = dict(layout_graph)
    graph = dict(layout_graph)
    inactiveNodes = []
    for i in initial_graph:
        if (availability_graph[i] != set(['ON'])):
            graph.pop(i)
            inactiveNodes.append(i)
    
    for key in graph:
        for i in inactiveNodes:
            try:
                graph[key].remove(i)
            except:
                pass

    try:
        graph[start]
    except:
        return ['no path exists']
    
    try:
        graph[end]
    except:
        return ['no path exists']

    print(graph)
    # maintain a queue of paths
    queue = []
    # push the first path into the queue
    queue.append([start])
    iters = 0
    while queue:
        
        
        iters = iters+1
        # get the first path from the queue
        path = queue.pop(0)
        print(iters)
        if (iters > max_iters):
            print('no path exists')
            return ['no path exists']
            # break
        # get the last node from the path
        nodeN = path[-1]
        # path found
        if nodeN == end:
            print('path found')
            return path
        # enumerate all adjacent nodes, construct a new path and push it into the queue
        for adjacent in graph.get(nodeN, []):
            new_path = list(path)
            new_path.append(adjacent)
            queue.append(new_path)

@uamethod
def add_node(parent,node,adjacent_nodes):
    # print('adding node begins')
    adjacent_nodes = set(adjacent_nodes)
    # print('adj set created')
    layout_graph.update({node:adjacent_nodes})
    # print('updated layout graph')
    availability_graph.update({node:set(['ON'])})
    # print('updated avail graph')
    for key in layout_graph:
        for adj in adjacent_nodes:
            if (key == adj):
                temp = set(layout_graph[key])
                temp.add(node)
                # print(temp)
                layout_graph.update({key:temp})

@uamethod
def make_node_offline(parent,node):
    availability_graph.update({node:set(['OFF'])})

# objects.add_method(1,'bfs',bfs)
# objects.add_method(1,'add_node',add_node)
# objects.add_method(1,'make_node_offline',make_node_offline)
GraphServer.addMethods([bfs,add_node,make_node_offline],['bfs','add_node','make_node_offline'])

# add_node('Test Node',set(['Lathe','KR16']))

# print(layout_graph)

    # for entry in layout_graph[key]:
    #     temp = layout_graph[key]
    #     if entry == 'KR10':
    #         layout_graph.update({key:})
        # pass




# @uamethod
# def get_path(parent, start_node, end_node):
#     return bfs(layout_graph,start_node,end_node)

            

# starting! The server will continue running
try:
    current_time = str(datetime.now().time())[:-7]
    print("{} - OPC UA server has been successfully initialised...".format(current_time))
    print("{} - Connect to OPC UA server via \"{}\"...".format(current_time, end_point))
    GraphServer.server.start()
except Exception as e:
    print("!!!ERROR!!! Failure to initialise the OPC UA server...")
    print(e)
    sys.exit()


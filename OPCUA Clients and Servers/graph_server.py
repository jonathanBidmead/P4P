import opcua
from opcua import uamethod
import paho.mqtt.client as mqtt
#TODO: get Sahil's server class in here

start_node = 'Linear Conveyor'
end_node = 'Platform'

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
'Linear Conveyor':'ON',
'KR16':'ON',
'Circular Conveyor':'ON',
'Platform':'ON',
'KR10':'ON',
'Lathe':'ON',
'Exit Platform':'ON'
}


def bfs(graph, start, end):
    # maintain a queue of paths
    queue = []
    # push the first path into the queue
    queue.append([start])
    while queue:
        # get the first path from the queue
        path = queue.pop(0)
        # get the last node from the path
        node = path[-1]
        # path found
        if node == end:
            return path
        # enumerate all adjacent nodes, construct a new path and push it into the queue
        for adjacent in graph.get(node, []):
            new_path = list(path)
            new_path.append(adjacent)
            queue.append(new_path)

@uamethod
def get_path(parent, start_node, end_node):
    return bfs(layout_graph,start_node,end_node)

            




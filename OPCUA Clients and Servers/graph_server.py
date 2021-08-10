# import opcua
# from opcua import uamethod
# import paho.mqtt.client as mqtt
#TODO: get Sahil's server class in here

start_node = 'Linear Conveyor'
end_node = 'KR10'

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


def bfs(graph, availability_graph, start, end):
    initial_graph = graph
    for i in initial_graph:#WIP: Removing OFF nodes from this copy of the grapht yui+
        if (availability_graph[i] != set(['ON'])):
            # graph.pop(i)
            print('popped')
    print(graph)

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

def add_node(node,adjacent_nodes):
    layout_graph.update({node:adjacent_nodes})
    availability_graph.update({node:'ON'})

def make_node_offline(node):
    availability_graph.update({node:'OFF'})


add_node('Test Node',set(['KR10','KR16']))
make_node_offline('KR10')
print(availability_graph)
# print(availability_graph)
# print()
# make_node_offline('KR10')
# print()
# print(availability_graph)

print(bfs(layout_graph,availability_graph,start_node,end_node))



# @uamethod
# def get_path(parent, start_node, end_node):
#     return bfs(layout_graph,start_node,end_node)

            




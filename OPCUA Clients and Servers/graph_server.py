from time import sleep
# import opcua
# from opcua import uamethod
# import paho.mqtt.client as mqtt
#TODO: get Sahil's server class in here

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


def bfs(graph: dict, availability_graph, start, end):
    initial_graph = dict(graph)
    falseFlags = []
    for i in initial_graph:#WIP: Removing OFF nodes from this copy of the graph
        if (availability_graph[i] != set(['ON'])):
            graph.pop(i)
            falseFlags.append(i)
    
    for key in graph:
        for i in falseFlags:
            try:
                graph[key].remove(i)
            except:
                pass

    print(graph)
    # maintain a queue of paths
    queue = []
    # push the first path into the queue
    queue.append([start])
    iters = 0
    while queue:
        if (len(queue) > 2*len(graph)):
            return []
            # break
        iters = iters+1
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
    availability_graph.update({node:set(['ON'])})
    for key in layout_graph:
        for adj in adjacent_nodes:
            if (key == adj):
                temp = set(layout_graph[key])
                temp.add(node)
                # print(temp)
                layout_graph.update({key:temp})


def make_node_offline(node):
    availability_graph.update({node:set(['OFF'])})


# add_node('Test Node',set(['Lathe','KR16']))
make_node_offline('Circular Conveyor')
# print(layout_graph)

    # for entry in layout_graph[key]:
    #     temp = layout_graph[key]
    #     if entry == 'KR10':
    #         layout_graph.update({key:})
        # pass
print(bfs(layout_graph,availability_graph,start_node,end_node))



# @uamethod
# def get_path(parent, start_node, end_node):
#     return bfs(layout_graph,start_node,end_node)

            




import sys
from urllib.request import DataHandler
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
import asyncio
import time
import datetime

#creating graph agent instance
graphAgent = smartServer.smartMqtt("graphAgent")

#creating/subscribing to pertinent mqtt topics
graphAgent.client.subscribe("/activeResources")
graphAgent.client.subscribe("/pathRequests")
graphAgent.client.subscribe("/keepAlivePings")

#creating graph describing the layout of all resources
layout_graph = dict()

lastTime = datetime.datetime.now()

#interuppt on receiving a message
def msg_func(client,userdata,msg):
    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)
    
    if(msg.topic == "/activeResources"):
        tempData = msg_decoded.split(",")
        if(msg_decoded[0:3] == "ADD"):
            # layout_graph[tempData[1]] = tempData[4].split()
            add_node(tempData[1],tempData[4].split())
        if(msg_decoded[0:3] == "DEL"):
            del_node(tempData[1])
        print(layout_graph)

    if(msg.topic == "/pathRequests"):
        tempData = msg_decoded.split(",")
        path = bfs(tempData[1],tempData[2])
        print(path)
        graphAgent.client.publish("/pathResponses",tempData[1] + "," + str(path))
    
    if(msg.topic == "/keepAlivePings"):
        if(msg_decoded == "PING"):
            agent = graphAgent
            agent.client.publish("/keepAlivePings",agent.name)


#defining msg_func (shortening variable names)
graphAgent.client.on_message = msg_func

#DEBUG: publish initial layout to activeResources topic (this will be offloaded to somewhere else eventually)
graphAgent.client.publish("/activeResources","ADD,LINEAR_CONVEYOR,BUFFER,-10 2,KR16")
graphAgent.client.publish("/activeResources","ADD,KR16,TRANSPORT,-5 2,LINEAR_CONVEYOR CIRCULAR_CONVEYOR PLATFORM")
graphAgent.client.publish("/activeResources","ADD,PLATFORM,BUFFER,-5 6,KR16")
graphAgent.client.publish("/activeResources","ADD,CIRCULAR_CONVEYOR,BUFFER,0 2,KR16,KR10")
graphAgent.client.publish("/activeResources","ADD,KR10,TRANSPORT,5 2,CIRCULAR_CONVEYOR LATHE EXIT_PLATFORM")
graphAgent.client.publish("/activeResources","ADD,LATHE,MACHINE,5 6,KR10")
graphAgent.client.publish("/activeResources","ADD,EXIT_PLATFORM,BUFFER,10 2,KR10")
#EVEN MORE DEBUG
graphAgent.client.publish("/activeResources","DEL,CIRCULAR_CONVEYOR")
# graphAgent.client.publish("/pathRequests","PART_AGENT_0,KR10,LINEAR_CONVEYOR")
#maximum search depth for bfs
max_iters = 256


#breadth-first search through the graph to find a path
def bfs(start, end):
    
    graph = dict(layout_graph)

    try:
        graph[start]
    except:
        return ['no path exists']
    
    try:
        graph[end]
    except:
        return ['no path exists']

    
    # maintain a queue of paths
    queue = []
    # push the first path into the queue
    queue.append([start])
    iters = 0
    while queue:
        
        
        iters = iters+1
        # get the first path from the queue
        path = queue.pop(0)
        
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

#adding a node - making sure it's adjacent to everything else
def add_node(node,adjacent_nodes):
    # print('adding node begins')
    adjacent_nodes = set(adjacent_nodes)
    # print('adj set created')
    layout_graph.update({node:adjacent_nodes})
    # print('updated layout graph')
    # availability_graph.update({node:set(['ON'])})
    # print('updated avail graph')
    for key in layout_graph:
        for adj in adjacent_nodes:
            if (key == adj):
                temp = set(layout_graph[key])
                temp.add(node)
                # print(temp)
                layout_graph.update({key:temp})

def del_node(node):
    layout_graph.pop(node)
    inactiveNodes = []
    inactiveNodes.append(node)

    for key in layout_graph:
        for i in inactiveNodes:
            try:
                layout_graph[key].remove(i)
            except:
                pass

#looping through everything
while True:
    #client loop for receiving mqtt messages
    graphAgent.client.loop(0.2)
    
    newTime = datetime.datetime.now()
    if (newTime - lastTime > datetime.timedelta(seconds=5)):
        graphAgent.client.publish("/keepAlivePings","PING")
        lastTime = datetime.datetime.now()


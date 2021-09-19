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
graphAgent.client.subscribe("/graphLogging")

#creating graph describing the layout of all resources
layout_graph = dict()

#time since last ping 
lastTime = datetime.datetime.now()

#currently active agents (according to ping responses)
activeAgents = []#TODO: Change to dict?

#offline agents (agents who've not responded to a ping but have been instantiated at some point)
offlineAgents = dict()

#agents that just got added
newAgents = []

#interuppt on receiving a message
def msg_func(client,userdata,msg):
    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)
    
    if(msg.topic == "/activeResources"):
        tempData = msg_decoded.split(",")
        if(msg_decoded[0:3] == "ADD"):
            if(tempData[1] not in layout_graph.keys() and tempData[1] not in offlineAgents.keys()):#only add a new node if it doesn't already exist
                add_node(tempData[1],tempData[4].split(),tempData[2],tempData[3])
                newAgents.append(tempData[1])

    if(msg.topic == "/pathRequests"):
        tempData = msg_decoded.split(",")
        path = bfs(tempData[1],tempData[2])
        print("Path Between Nodes" + str(path))
        graphAgent.client.publish("/pathResponses",tempData[1] + "," + str(path))
    
    #pinging response (copy paste this to other servers)
    if(msg.topic == "/keepAlivePings"):
        if(msg_decoded == "PING"):
            agent = graphAgent#replace with current agent (and uncomment the below line)
            # agent.client.publish("/keepAlivePings",agent.name)

    #pinging response (graph server only)
    if(msg.topic == "/keepAlivePings"):
        if(msg_decoded != "PING"):
            #if the server has seen this node before and it was previously online
            if (msg_decoded in layout_graph.keys() and msg_decoded not in activeAgents and msg_decoded not in offlineAgents.keys()):
                activeAgents.append(msg_decoded)
            #if this node was previously offline
            if (msg_decoded in offlineAgents.keys()):
                make_node_online(msg_decoded)
                activeAgents.append(msg_decoded)


#defining msg_func (shortening variable names)
graphAgent.client.on_message = msg_func

#maximum search depth for bfs
max_iters = 256

#number of seconds machines have to respond to a ping before being considered offline
PINGING_TIMEOUT = 5#not used currently,. current implementation is to give each resource until the next ping happens to respond
PING_FREQUENCY = 5

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



#adding a node - making sure it's adjacent to everything else it needs to be
def add_node(node,adjacent_nodes,type,GUI_location):
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
    #logging this action
    adj_str = ""
    #reformatting the adjacent nodes to a string
    for nd in adjacent_nodes:
        adj_str = adj_str + nd + " "
    adj_str = adj_str.rstrip(" ")
    graphAgent.client.publish("/graphLogging","ADD," + str(node) + "," + type + "," + GUI_location + "," + adj_str)


#deleting a node permanently
def del_node(node,asOffline):
    layout_graph.pop(node)
    inactiveNodes = []
    inactiveNodes.append(node)

    for key in layout_graph:
        for i in inactiveNodes:
            try:
                layout_graph[key].remove(i)
            except:
                pass
    #logging this action
    if(not asOffline):
        graphAgent.client.publish("/graphLogging","DEL," + str(node))

#temporarily marking a node as offline when it stops responding to pings
def make_node_offline(node):
    if(node not in offlineAgents):
        offlineAgents[node] = layout_graph[node]#get node and adjacents and put that in the new dict
        print("made node offline: " + str(node))
        del_node(node,True)
    #logging this action
    graphAgent.client.publish("/graphLogging","OFF," + str(node))

#re-instantiate a node once it starts returning pings again
def make_node_online(node):
    layout_graph[node] = offlineAgents[node]
    offlineAgents.pop(node)
    #logging this action
    graphAgent.client.publish("/graphLogging","ON," + str(node))

#initial ping
graphAgent.client.publish("/keepAlivePings","PING")

#temp debug solution
loops = 0

#looping through everything
while True:
    #client loop for receiving mqtt messages
    graphAgent.client.loop(0.2)
    
    #DEBUG
    # print("active agents" + str(activeAgents))

    #send a ping every so often to figure out what agents are still active
    newTime = datetime.datetime.now()
    if (newTime - lastTime > datetime.timedelta(seconds=PING_FREQUENCY)):
        graphAgent.client.publish("/keepAlivePings","PING")
        lastTime = datetime.datetime.now()
        
        #initial loop fucks it up a bit so skipping (this is an early remnant so may be unnecessary now)
        if (loops < 1):
            loops += 1
            continue
        

        temp_layout_dict = dict(layout_graph)
        print("active agents" + str(activeAgents))
        for key in temp_layout_dict:
            if (key not in activeAgents and key not in offlineAgents.keys()):#if an agent in layout_graph hasn't responded to ping & hasn't previously been marked offline, make it be offline
                # graphAgent.client.publish("/activeResources","OFF"+","+key)
                if (key not in newAgents):
                    make_node_offline(key)
        # print(layout_graph)
        activeAgents = []
        newAgents = []



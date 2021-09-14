import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
import asyncio
import time
import datetime


#creating graph agent instance
loggingAgent = smartServer.smartMqtt("loggingAgent")

#creating/subscribing to pertinent mqtt topics
loggingAgent.client.subscribe("/activeResources")
loggingAgent.client.subscribe("/pathRequests")

#for reference: what text files even exist?
# agent_locations - All resource agent locations in the GUI
# buffer_agents    - List of Resource Agent Associated Names that are Buffer Type
# machine_agents - List of Resource Agent Associated Names that are Machine Type
# transport_agents - List of Resource Agent Associated Names that are Transport Type
# layout_graph - List of all Resource Agents and Associated Adjacent Agents
# part_agent_log - List of all Part Agent Locations at various timesteps

#if I receive a message from activeResources, what text file do I write that to?

#treat all resource agents being added to the thing before and part  agents are instantiated as the initial graph
is_initial_graph = True

def msg_func(client,userdata,msg):
    msg_decoded = msg.payload.decode("utf-8")
    file = open("test_log.txt","a")
    file.write("Received message: " + msg.topic + " -> " + msg_decoded + '\n')
    file.close()
    if(msg.topic == "/activeResources"):
        if (is_initial_graph):

            if(msg_decoded[0:3] == "ADD"):
                tempData = msg_decoded.split(",")
                file = open("test_initial_layout_graph.txt","a")
                adjacent_list = tempData[4].split()
                adj_string = ""
                for agent in adjacent_list:
                    adj_string = adj_string + "," + agent
                file.write(tempData[1]+adj_string+"\n")
                file.close()
            
            if(msg_decoded[0:3] == "DEL"):
                pass#TODO: Implement, gonna be a bit of a pain because need to remove adjacencies from all nodes, not just the deleted one
    

#defining msg_func (shortening variable names)
loggingAgent.client.on_message = msg_func

#initially clear the log file
f = open("test_log.txt","w")
f.write("")
f.close()

f = open("test_initial_layout_graph.txt","w")
f.write("")
f.close()

while True:
    loggingAgent.client.loop(0.1)


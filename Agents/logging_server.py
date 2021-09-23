import sys
from typing import NewType
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
import asyncio
import time
import datetime


#creating graph agent instance
loggingAgent = smartServer.smartMqtt("loggingAgent")

#creating/subscribing to pertinent mqtt topics
loggingAgent.client.subscribe("/graphLogging")
loggingAgent.client.subscribe("/pathRequests")
loggingAgent.client.subscribe("/partAgentLogging")
loggingAgent.client.subscribe("/pathResponses")
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
    file.write("at " + str(datetime.datetime.now()) + " Received message: " + msg.topic + " -> " + msg_decoded + '\n')
    file.close()
    if(msg.topic == "/graphLogging"):
        if (is_initial_graph):
            if(msg_decoded[0:3] == "ADD"):
                tempData = msg_decoded.split(",")

                file = open("test_initial_layout_graph.txt","r")
                allText = file.readlines()

                #variable to check if agent exists already
                agentExists = False

                for line in allText:#for each line in the file
                    elements = line.split(",")
                    if (elements[0] == tempData[1]):#check if the first element in the line is the item to be added
                        #agent already exists, don't add a duplicate
                        agentExists = True
                
                file.close()

                if(agentExists == False):
                    file = open("test_initial_layout_graph.txt","a")
                    adjacent_list = tempData[4].split()
                    adj_string = ""
                    for agent in adjacent_list:
                        adj_string = adj_string + "," + agent
                    file.write(tempData[1]+","+tempData[3]+adj_string+"\n")
                    file.close()
                    print("adding line to initial graph")
            
            if(msg_decoded[0:3] == "DEL" or msg_decoded[0:3] == "OFF"):
                tempData = msg_decoded.split(",")
                file = open("test_initial_layout_graph.txt","r")
                allText = file.readlines()
                for line in allText:#for each line in the file
                    elements = line.split(",")
                    if (elements[0] == tempData[1]):#check if the first element in the line is the item to be deleted
                        print("delete line: " + line)

                file.close()

        if (not is_initial_graph):
            file = open("test_ongoing_layout_graph.txt","a")
            file.write(str(datetime.datetime.now()) + ",")
            file.write(msg_decoded + '\n')
            file.close()
            print("ongoing update")

    if(msg.topic == "/partAgentLogging"):
        file = open("test_part_agent_log.txt","a")
        file.write(str(datetime.datetime.now()) + ",")
        file.write(msg_decoded + '\n')
        file.close()
        print("part agent movement")


    

#defining msg_func (shortening variable names)
loggingAgent.client.on_message = msg_func

#initially clear the log files
f = open("test_log.txt","w")
f.write("")
f.close()

f = open("test_initial_layout_graph.txt","w")
f.write("")
f.close()

f = open("test_ongoing_layout_graph.txt","w")
f.write("")
f.close()

f = open("test_part_agent_log.txt","w")
f.write("")
f.close()


initTime = datetime.datetime.now()

while True:
    loggingAgent.client.loop(0.1)

    if(datetime.datetime.now() - initTime > datetime.timedelta(seconds=15)):#TODO: make a better condition for switching from initialisation/setup to ongoing updates
        is_initial_graph = False


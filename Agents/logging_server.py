import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
import asyncio
import time


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


def msg_func(client,userdata,msg):
    msg_decoded = msg.payload.decode("utf-8")
    file = open("test_log.txt","a")
    file.write("Received message: " + msg.topic + " -> " + msg_decoded + '\n')
    file.close()
    

#defining msg_func (shortening variable names)
loggingAgent.client.on_message = msg_func



while True:
    loggingAgent.client.loop(0.1)


import sys
from time import sleep
from urllib.request import DataHandler
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer

#creating graph agent instance
dummyAgent = smartServer.smartMqtt("DUMMY_AGENT")

#creating/subscribing to pertinent mqtt topics
dummyAgent.client.subscribe("/activeResources")
dummyAgent.client.subscribe("/pathRequests")
dummyAgent.client.subscribe("/keepAlivePings")

def msg_func(client,userdata,msg):
    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)

    #pinging response (copy paste this to other servers)
    if(msg.topic == "/keepAlivePings"):
        if(msg_decoded == "PING"):
            agent = dummyAgent#replace with current agent
            agent.client.publish("/keepAlivePings",agent.name)
            agent.client.publish("/keepAlivePings","KR16")
            agent.client.publish("/keepAlivePings","LINEAR_CONVEYOR")

#defining msg_func (shortening variable names)
dummyAgent.client.on_message = msg_func

dummyAgent.client.publish("/activeResources","ADD,DUMMY_AGENT,BUFFER,0 0,KR10,LINEAR_CONVEYOR")

#DEBUG: publish initial layout to activeResources topic (this will be offloaded to somewhere else eventually)
dummyAgent.client.publish("/activeResources","ADD,LINEAR_CONVEYOR,BUFFER,-10 2,KR16")
dummyAgent.client.publish("/activeResources","ADD,KR16,TRANSPORT,-5 2,LINEAR_CONVEYOR CIRCULAR_CONVEYOR PLATFORM")
# dummyAgent.client.publish("/activeResources","ADD,PLATFORM,BUFFER,-5 6,KR16")
# dummyAgent.client.publish("/activeResources","ADD,CIRCULAR_CONVEYOR,BUFFER,0 2,KR16,KR10")
# dummyAgent.client.publish("/activeResources","ADD,KR10,TRANSPORT,5 2,CIRCULAR_CONVEYOR LATHE EXIT_PLATFORM")
# dummyAgent.client.publish("/activeResources","ADD,LATHE,MACHINE,5 6,KR10")
# dummyAgent.client.publish("/activeResources","ADD,EXIT_PLATFORM,BUFFER,10 2,KR10")

while True:
    dummyAgent.client.loop(0.1)

    sleep(10)
    dummyAgent.client.publish("/movement","PART_AGENT_0,NODE1,NODE2")
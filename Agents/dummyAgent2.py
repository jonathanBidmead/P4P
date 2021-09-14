import sys
from urllib.request import DataHandler
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer

#creating graph agent instance
dummyAgent = smartServer.smartMqtt("DUMMY_AGENT2")

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
            agent.client.publish("/keepAlivePings","PLATFORM")
            agent.client.publish("/keepAlivePings","LATHE")
            agent.client.publish("/keepAlivePings","CIRCULAR_CONVEYOR")

#defining msg_func (shortening variable names)
dummyAgent.client.on_message = msg_func


#DEBUG: publish initial layout to activeResources topic (this will be offloaded to somewhere else eventually)
dummyAgent.client.publish("/activeResources","ADD,PLATFORM,BUFFER,-5 6,KR16")
dummyAgent.client.publish("/activeResources","ADD,CIRCULAR_CONVEYOR,BUFFER,0 2,KR16,KR10")
dummyAgent.client.publish("/activeResources","ADD,LATHE,MACHINE,5 6,KR10")

while True:
    dummyAgent.client.loop(0.1)
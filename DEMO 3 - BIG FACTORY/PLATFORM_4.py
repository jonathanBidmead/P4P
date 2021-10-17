import sys
from time import sleep
from urllib.request import DataHandler
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
import datetime
#creating graph agent instance
agentName = "PLATFORM_4"
guiLocation = "4 4"
adjacents = "KR10_4 KR10_3"
agent = smartServer.smartMqtt(agentName)#CHANGE

#creating/subscribing to pertinent mqtt topics
agent.client.subscribe("/activeResources")
agent.client.subscribe("/pathRequests")
agent.client.subscribe("/keepAlivePings")
agent.client.subscribe("/isResourceAvailable")

def msg_func(client,userdata,msg):
    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)

    #pinging response (copy paste this to other servers)
    if(msg.topic == "/keepAlivePings"):
        if(msg_decoded == "PING"):
            print("responding to ping")
            agent.client.publish("/keepAlivePings",agent.name)

    if(msg.topic == "/isResourceAvailable"):
        tempData = msg_decoded
        print(tempData)
        if(tempData == agent.name):
            agent.client.publish("/isResourceAvailable",agent.name + ",YES")

#defining msg_func (shortening variable names)
agent.client.on_message = msg_func

#add self to graph
agent.client.publish("/activeResources","ADD," + agent.name + ",BUFFER," + guiLocation + "," + adjacents)

while True:
    agent.client.loop(0.5)
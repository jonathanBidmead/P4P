import sys
from time import sleep
from urllib.request import DataHandler
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
import datetime
#creating graph agent instance
agent = smartServer.smartMqtt("BUFFER_1")#CHANGE
score = 10000

#creating/subscribing to pertinent mqtt topics
agent.client.subscribe("/activeResources")
agent.client.subscribe("/pathRequests")
agent.client.subscribe("/keepAlivePings")
agent.client.subscribe("/isResourceAvailable")
agent.client.subscribe("/partBids")

def msg_func(client,userdata,msg):
    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)
    msg_split = msg_decoded.split(",")

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

    if(msg.topic == "/partBids"):
        agent.client.publish("/machineBids",agent.name + "," + str(score) + "," + msg_split[0])


#defining msg_func (shortening variable names)
agent.client.on_message = msg_func

#add self to graph
agent.client.publish("/activeResources","ADD,BUFFER1,BUFFER,-5 6,KR16")#CHANGE

while True:
    agent.client.loop(0.1)
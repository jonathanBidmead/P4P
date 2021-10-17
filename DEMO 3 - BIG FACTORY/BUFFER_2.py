import sys
from time import sleep
from urllib.request import DataHandler
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
import datetime
import time

#creating graph agent instance
agentName = "BUFFER_2"#CHANGE
adjacents = "KR10_5 KR10_6 KR10_7"#CHANGE
guiLocation = "0 -5.5"#CHANGE
agent = smartServer.smartMqtt(agentName)
score = 10000

currentTime = 0
prevTime = 0

part_list = []
acceptingBids = True

#creating/subscribing to pertinent mqtt topics
agent.client.subscribe("/activeResources")
agent.client.subscribe("/pathRequests")
agent.client.subscribe("/keepAlivePings")
agent.client.subscribe("/isResourceAvailable")
agent.client.subscribe("/partBids")
agent.client.subscribe("/machineBids")

def msg_func(client,userdata,msg):
    global acceptingBids
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

    if(msg.topic == "/partBids" and acceptingBids):
        part_list.append((msg_split[0],float(msg_split[1])))
    

#defining msg_func (shortening variable names)
agent.client.on_message = msg_func

#add self to graph
agent.client.publish("/activeResources","ADD," + agentName + ",BUFFER," + guiLocation + "," + adjacents)

while True:
    agent.client.loop(0.5)

    if(len(part_list) == 0):
        prevTime = time.time()
        currentTime = prevTime
        while(currentTime - prevTime < 1):
            currentTime = time.time()
            agent.client.loop(0.5)
    else:
        acceptingBids = False
        part_list.sort(key = lambda x:x[1],reverse = True)
        agent.client.publish("/machineBids",agent.name + "," + str(score) + "," + part_list[0][0])
        prevTime = time.time()
        currentTime = prevTime
        while(currentTime - prevTime < 10):
            currentTime = time.time()
            agent.client.loop(0.5)
        part_list = []
        acceptingBids = True





    
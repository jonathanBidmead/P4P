import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
from MultiAgent import smartServer
import asyncio
import time

#msgs
msg_auctions = []
msg_publish = []
#Message format:
# /agentName


def msg_func(client,userdata,msg):
    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)
    
    msg_split = msg_decoded.split("/")
    requestedTask = msg_split[1]
    

    if(msg.topic == "/auction"):
        for func in functions:
            if(requestedTask == func):
                latheAgent.client.publish("/bids","lathe2/yes!")
                latheAgent.client.loop(0.1)
                break
            

    


latheAgent = smartServer.smartMqtt("lathe2")
latheAgent.client.subscribe("/auction")
latheAgent.client.subscribe("/bids")
latheAgent.client.on_message = msg_func

#Flags
published = False

#Tasks
functions = ["lathe"]

waitTime = 5
currTime = 0
prevTime = 0

latheAgent.client.loop_forever()
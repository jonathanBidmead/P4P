import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
import asyncio
import time


graphClient = smartServer.smartOpcua("localhost",7005,"graphClient","client")
##make one common function for each server that maps other fucntions internally
bfs = graphClient.methods[2]

latheClient = smartServer.smartOpcua("localhost",4002,"lathe","client")
req = latheClient.methods[2]

clients = {
    "lathe1":latheClient
}


#msgs
msg_bids = []
msg_publish = []
#Message format:
# /whoisthisfrom/information


def msg_func(client,userdata,msg):
    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)
    
    msg_split = msg_decoded.split("/")
    agentName = msg_split[0]
    

    if(msg.topic == "/bids"):
        msg_bids.append(agentName)

    


partAgent = smartServer.smartMqtt("partAgent")
partAgent.client.subscribe("/auction")
partAgent.client.subscribe("/bids")
partAgent.client.on_message = msg_func

#Flags
published = False

#Tasks
tasks = ["lathe","output basket"]

waitTime = 5
currTime = 0
prevTime = 0

while True:
    partAgent.client.loop(0.2)
    if(not published):
        msg_bids = []
        partAgent.client.publish("/auction","partAgent/" + tasks[0])
        published = True
        
        prevTime = time.time()
        currTime = prevTime
        while(currTime-prevTime < waitTime):
            partAgent.client.loop(0.1)
            currTime = time.time()

        print(msg_bids)

        #Selection of machine
        if(len(msg_bids) > 0):
            chosen = msg_bids[0]

            path = graphClient.objects.call_method(bfs,'Linear Conveyor','Lathe')
            print(path)
            

            #Need a way to map the client and servers to a list or something
            respone = clients[chosen].objects.call_method(req,'Available')
            if(respone == True):
                print("Requesting lathe1 to thread")
                respone = clients[chosen].objects.call_method(req,"Thread")
                tasks.pop(0)
                print("Threading complete")

            
            published = False
            msg_bids = []
            continue


        else:
            published = False
            continue
        

        

    
    


    
    
    
















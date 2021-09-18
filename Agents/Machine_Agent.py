import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
from opcua import uamethod
import asyncio
import time

#OPCUA stuff to be implemented later. Refer to Lathe1.py for implementing OPCUA stuff

#Variables and Flags
machineBooked = False
partBids = []
acceptingBids = True
currentTime = 0
prevTime = 0
confirmationRecieved = False
operationRequest = False

machineName = "lathe1"




def msg_func(client,userdata,msg):
    global acceptingBids
    global partBids
    global machineBooked
    global operationRequest

    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)
    topic = msg.topic
    msg_split = msg_decoded.split("/")

    if(topic == "/partBids"):
        if(acceptingBids and msg_split[2] == "lathe"): #decide on location of if the agent mentions lathe
            partBids.append(msg_split[3]) #Decide on message format

    if(topic == "/machining"):
        if(msg_split[2] == "this specific machine"): #Decide on format of message 
            if(machineBooked):
                operationRequest = True
    
    if(topic = "/")
    #All movemement agent requests can be added here too. Directly call the OPCUA methods

        

            
#MQTT setup
latheAgent = smartServer.smartMqtt(machineName)
latheAgent.client.subscribe("/partBids")
latheAgent.client.subscribe("/machineBids")
latheAgent.client.subscribe("/machining")
latheAgent.client.subscribe("/partAgents")
latheAgent.client.on_message = msg_func

while True:
    latheAgent.client.loop(0.1)

    if(not machineBooked):
        if(acceptingBids):
            #If machine is accepting bids and hasnt been booked
            prevTime = time.time()
            currentTime = prevTime
            while(currentTime - prevTime < 5):
                currentTime = time.time()
                latheAgent.client.loop(0.1)
            
            if(len(partBids) != 0):
                acceptingBids = False

        else:
            #If machine has recieved a list of bids
            partBids.sort(key = lambda x:x[1])
            chosenPart = partBids[0]
            latheAgent.client.publish("/machineBids","/" + chosenPart + "/Chosen") #Decide msg pattern
            prevTime = time.time()
            currentTime = prevTime
            while(currentTime - prevTime < 5):
                currentTime = time.time()
                latheAgent.client.loop(0.1)
            if(confirmationRecieved == True):
                machineBooked = True
            else:
                acceptingBids = True
                partBids = []
    
    else:
        if(operationRequest):
            latheAgent.client.publish("/partAgents" + chosenPart + "/Completed")
            machineBooked = False
            partBids = []
            acceptingBids = True
            currentTime = 0
            prevTime = 0
            confirmationRecieved = False
            operationRequest = False
                    



            




                






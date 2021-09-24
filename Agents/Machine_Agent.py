import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
from opcua import uamethod
import asyncio
import time

#OPCUA stuff to be implemented later. Refer to Lathe1.py for implementing OPCUA stuff

#Variables and Flags
machineCapabilites = ["LATHE"]
machineBooked = False
partBids = []
acceptingBids = True
currentTime = 0
prevTime = 0
confirmationRecieved = False
operationRequest = False
speed = 100
chosenPart = ("",0)

machineName = "LATHE"

def reset():
    global machineBooked
    global partBids
    global acceptingBids
    global confirmationRecieved
    global operationRequest
    global chosenPart

    machineBooked = False
    partBids = []
    acceptingBids = True
    confirmationRecieved = False
    operationRequest = False
    chosenPart = ("",0)



def msg_func(client,userdata,msg):
    global acceptingBids
    global partBids
    global machineBooked
    global operationRequest
    global chosenPart
    global confirmationRecieved

    msg_decoded = msg.payload.decode("utf-8")
    # print("Received message: " + msg.topic + " -> " + msg_decoded)
    topic = msg.topic
    msg_split = msg_decoded.split(",")

    if(topic == "/partBids"):
        if(acceptingBids and (msg_split[2] in machineCapabilites)):
            #Implement the bit where it ignores same agents
            partBids.append((msg_split[0],float(msg_split[1])))
            
    if(topic == "/confirmation"):
        if((not acceptingBids) and (not machineBooked)): 
            if(msg_split[1] == machineName): #Add a check to see if the message is coming from the expected part agent?
                confirmationRecieved = True

    if(topic == "/machining"):
        print("------------")
        print(msg_split)
        print(machineName)
        print(chosenPart)
        print("--------------------")
        if(msg_split[1] == machineName and msg_split[0] == chosenPart[0]):
            print("MachineBooked: " + str(machineBooked))
            if(machineBooked):
                operationRequest = True

    if(msg.topic == "/keepAlivePings"):
        if(msg_decoded == "PING"):
            print("responding to ping")
            agent = latheAgent#replace with current agent
            agent.client.publish("/keepAlivePings",agent.name)
    
    if(msg.topic == "/cancellation" and msg_split[0] == chosenPart[0] and msg_split[1] == machineName):
        print("Contract Cancelled")
        reset()

    if(msg.topic == "/isResourceAvailable"):
        agent = latheAgent
        if(msg_decoded == agent.name):
            agent.client.publish("/isResourceAvailable",agent.name + ",YES")

    

        

            
#MQTT setup
latheAgent = smartServer.smartMqtt(machineName)
latheAgent.client.subscribe("/partBids")
latheAgent.client.subscribe("/machineBids")
latheAgent.client.subscribe("/machining")
latheAgent.client.subscribe("/partAgents")
latheAgent.client.subscribe("/confirmation")
latheAgent.client.subscribe("/keepAlivePings")
latheAgent.client.subscribe("/activeResources")
latheAgent.client.subscribe("/cancellation")
latheAgent.client.subscribe("/isResourceAvailable")
latheAgent.client.on_message = msg_func

#adding to graph agent
latheAgent.client.publish("/activeResources","ADD,LATHE,MACHINE,5 6,KR10")

while True:
    latheAgent.client.loop(0.1)

    if(not machineBooked):
        if(acceptingBids):
            #If machine is accepting bids and hasnt been booked
            print("Accepting Bids")
            prevTime = time.time()
            currentTime = prevTime
            while(currentTime - prevTime < 5):
                currentTime = time.time()
                latheAgent.client.loop(0.1)
            
            if(len(partBids) != 0):
                print("Bids recieved!")
                acceptingBids = False
            else:
                print("No bids recieved")

        else:
            #If machine has recieved a list of bids
            print("Processing Bids")
            partBids.sort(key = lambda x:x[1],reverse=True)
            chosenPart = partBids[0]
            latheAgent.client.publish("/machineBids",machineName + "," + str(speed) + "," + chosenPart[0]) #Decide msg pattern
            prevTime = time.time()
            currentTime = prevTime
            while(currentTime - prevTime < 10): #Needs to be longer than the part agent wait time
                if(confirmationRecieved):
                    break
                currentTime = time.time()
                latheAgent.client.loop(0.1)
            if(confirmationRecieved == True):
                print("3-way handshake complete")
                machineBooked = True 
            else:
                acceptingBids = True
                partBids = []
    
    else:
        if(operationRequest):
            print("Operation completed")
            latheAgent.client.publish("/confirmation",machineName + "," + chosenPart[0] + "," + "done")
            machineBooked = False
            partBids = []
            acceptingBids = True
            currentTime = 0
            prevTime = 0
            confirmationRecieved = False
            operationRequest = False
                    



            




                





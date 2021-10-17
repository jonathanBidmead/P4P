import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
from opcua import uamethod
import asyncio
import time

#OPCUA stuff to be implemented later. Refer to Lathe1.py for implementing OPCUA stuff

#Variables and Flags
machineCapabilites = ["MILL"]
machineBooked = False
partBids = []
acceptingBids = True
currentTime = 0
prevTime = 0
confirmationRecieved = False
operationRequest = False
chosenPart = ("",0)
partInMachine = "none"

#CHANGE THESE THINGS
machineName = "MILL_3"#CHANGE
guiLocation = "-8 -3.5"
adjacents = "KR10_5"
speed = 20


currentlyProcessing = False

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
    global partInMachine
    global currentlyProcessing


    msg_decoded = msg.payload.decode("utf-8")
    # print("Received message: " + msg.topic + " -> " + msg_decoded)
    topic = msg.topic
    msg_split = msg_decoded.split(",")
    if (not currentlyProcessing or topic == "/keepAlivePings"):
        # print("processing in msgfunc")
        # if (topic != "/keepAlivePings"):
        #     pass

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
                agent = machineAgent#replace with current agent
                agent.client.publish("/keepAlivePings",agent.name)
        
        if(msg.topic == "/cancellation" and msg_split[0] == chosenPart[0] and msg_split[1] == machineName):
            print("Contract Cancelled")
            reset()

        if(msg.topic == "/isResourceAvailable"):
            agent = machineAgent
            if(msg_decoded == agent.name):
                agent.client.publish("/isResourceAvailable",agent.name + ",YES")

        if(msg.topic == "/partAgentLogging"):
            if(partInMachine == "none"):
                if(msg_split[1] == machineName):
                    partInMachine = msg_split[0]
            else:
                if(msg_split[0] == partInMachine):
                    if(msg_split[1] != machineName):
                        partInMachine = "none"

    

        

            
#MQTT setup
machineAgent = smartServer.smartMqtt(machineName)
machineAgent.client.subscribe("/partBids")
machineAgent.client.subscribe("/machineBids")
machineAgent.client.subscribe("/machining")
machineAgent.client.subscribe("/partAgents")
machineAgent.client.subscribe("/confirmation")
machineAgent.client.subscribe("/keepAlivePings")
machineAgent.client.subscribe("/activeResources")
machineAgent.client.subscribe("/cancellation")
machineAgent.client.subscribe("/isResourceAvailable")
machineAgent.client.subscribe("/partAgentLogging")
machineAgent.client.on_message = msg_func

#adding to graph agent
machineAgent.client.publish("/activeResources","ADD," + machineName + ",MACHINE," + guiLocation + "," + adjacents)

while True:
    machineAgent.client.loop(0.5)

    if(not machineBooked):
        if(acceptingBids):
            if(partInMachine != "none"):
                pass
            else:
                print("Accepting Bids")
                prevTime = time.time()
                currentTime = prevTime
                while(currentTime - prevTime < 1):
                    currentTime = time.time()
                    machineAgent.client.loop(0.1)
                
                if(len(partBids) != 0):
                    print("Bids recieved!")
                    acceptingBids = False
                else:
                    print("No bids recieved")

        else:
            #If machine has recieved a list of bids
            print("Processing Bids")
            partBids.sort(key = lambda x:x[1])
            chosenPart = partBids[0]
            machineAgent.client.publish("/machineBids",machineName + "," + str(speed) + "," + chosenPart[0]) #Decide msg pattern
            prevTime = time.time()
            currentTime = prevTime
            while(currentTime - prevTime < 10):
                if(confirmationRecieved):
                    break
                currentTime = time.time()
                machineAgent.client.loop(0.1)
            if(confirmationRecieved == True):
                print("3-way handshake complete")
                machineBooked = True 
            else:
                acceptingBids = True
                partBids = []
    
    else:
        if(operationRequest):
            prevTime = time.time()
            currentTime = prevTime
            currentlyProcessing = True
            while(currentTime - prevTime < speed):#DEBUG: SIMULATING A LONG PROCESS
                currentTime = time.time()
                machineAgent.client.loop(0.1)
            currentlyProcessing = False
            machineAgent.client.publish("/confirmation",machineName + "," + chosenPart[0] + "," + "done")
            print("Operation completed")
            machineBooked = False
            partBids = []
            acceptingBids = True
            currentTime = 0
            prevTime = 0
            confirmationRecieved = False
            operationRequest = False
            
                    



            




                






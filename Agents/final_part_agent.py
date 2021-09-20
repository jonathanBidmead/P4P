import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
from opcua import uamethod
import asyncio
import time
import enum


#OPCUA stuff to be implemented later. Refer to Lathe1.py for implementing OPCUA stuff

class States(enum.Enum):
    acceptingBids = 1


#Variables and Flags
agentName = sys.argv[1]
taskList = ["Lathe","task2"]
currentTask = ""
taskDone = False
machineList = []
currentTime = 0
prevTime = 0
score = float(sys.argv[2])
state = ""
targetPath = []
currentNode = "Linear Conveyer"
targetNode = ""





def msg_func(client,userdata,msg):
    global state

    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)
    topic = msg.topic
    msg_split = msg_decoded.split(",")

    if(topic == "/machineBids"):
        if(state == States.acceptingBids):
            if(msg_split[2] == agentName):
                machineList.append((msg_split[0],float(msg_split[1])))


            
#MQTT setup
partAgent = smartServer.smartMqtt(agentName)
partAgent.client.subscribe("/partBids")
partAgent.client.subscribe("/machineBids")
partAgent.client.subscribe("/machining")
partAgent.client.subscribe("/partAgents")
partAgent.client.subscribe("/confirmation")
partAgent.client.subscribe("/pathRequests")
partAgent.client.on_message = msg_func

while (len(taskList) != 0):
    partAgent.client.loop(0.1)

    currentTask = taskList[0]

    if(taskDone):
        print("Task done, removing from list")
        taskList.pop(0) #Remove the first task in the list
        taskDone = False
    
    else:
        if(len(machineList) == 0):
        #Creating auction
            print("Starting auction for machines")
            state = States.acceptingBids
            partAgent.client.publish("/partBids",agentName + "," + str(score) + "," + currentTask)
            currentTime = time.time()
            prevTime = currentTime
            while(currentTime - prevTime < 10): # Wait time needs to be double the machine time?
                partAgent.client.loop(0.1)
                currentTime = time.time()
        
        else:
            print("Machine chosen, going to machine now...")
            machineList.sort(key = lambda x:x[1])
            state = "" #Doesn't matter what this is.
            chosenMachine = machineList[0]  #Based on machining time    
            partAgent.client.publish("/confirmation",agentName + "," + chosenMachine[0] + "," +  "You are chosen")
            partAgent.client.publish("/pathRequests",agentName + "," + currentNode + "," + targetNode)


            #Reset for now
            taskList = []


            #wait to recieve response amd do graph stuff....pygame.examples.mask.main()



            
            


        




    

    

 




            




                






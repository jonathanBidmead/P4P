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
    findingPath = 2
    followingPath = 3


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

def reset():
    global currentTask
    global taskDone
    global machineList
    global state
    global targetPath

    currentTask = ""
    taskDone = False
    machineList = []
    state = ""
    targetPath = []


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
    
    if(topic == "/pathRequests"):
        if(state == States.findingPath):
            #Append to target path
            pass

    if(topic == "/movement"):
        if(state == States.followingPath):
            #Work this out
            pass



            
#MQTT setup
partAgent = smartServer.smartMqtt(agentName)
partAgent.client.subscribe("/partBids")
partAgent.client.subscribe("/machineBids")
partAgent.client.subscribe("/machining")
partAgent.client.subscribe("/partAgents")
partAgent.client.subscribe("/confirmation")
partAgent.client.subscribe("/pathRequests")
partAgent.client.subscribe("/movement")
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
            #Sends confirmation to chosen machine
            #------------------------------------------------------------------------
            print("Machine chosen, going to machine now...")
            machineList.sort(key = lambda x:x[1])
            state = States.findingPath #Doesn't matter what this is.
            chosenMachine = machineList[0]  #Based on machining time    
            partAgent.client.publish("/confirmation",agentName + "," + chosenMachine[0] + "," +  "You are chosen")
            #--------------------------------------------------------------------------------


            #Start to follow path to target node (chosen Machine)
            #-----------------------------------------------------------------------------------
            targetNode = chosenMachine
            while(currentNode != targetNode):
                targetPath = []
                partAgent.client.publish("/pathRequests",agentName + "," + currentNode + "," + targetNode)
                while(len(targetPath) == 0): #Waits till a response is recieved from the graph agent
                    partAgent.client.loop(0.1)

                if(targetPath[0] == "no path exists"):
                    reset()
                    print("No path found, going to auction again :(")
                    break
                else:
                    state = States.followingPath
                    #Need to talk to jonathan about how this is gonna work
                    partAgent.client.publish("/movement",agentName + "," + targetPath[0] + "," + currentNode + "," + )

            #-----------------------------------------------------------------------------------------
            

            #Once, target node is reached request for operation and set taskDone = True
            reset()
            taskDone = True




            
            


        




    

    

 




            




                






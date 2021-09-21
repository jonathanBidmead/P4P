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
    atMachine = 4


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
movementMachine = ""
movementStarted = False
movementFinished = False

def reset():
    global currentTask
    global taskDone
    global machineList
    global state
    global targetPath
    global movementMachine
    global movementStarted
    global movementFinished

    currentTask = ""
    taskDone = False
    machineList = []
    state = ""
    targetPath = []
    movementMachine = ""
    movementStarted = False
    movementFinished = False


def msg_func(client,userdata,msg):
    global state
    global targetPath
    global movementFinished
    global movementStarted
    global currentNode
    global movementMachine
    global taskDone

    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)
    topic = msg.topic
    msg_split = msg_decoded.split(",")

    if(topic == "/machineBids"):
        if(state == States.acceptingBids):
            if(msg_split[2] == agentName):
                machineList.append((msg_split[0],float(msg_split[1])))
    
    if(topic == "/pathResponses"):
        if(state == States.findingPath and msg_split[0] == agentName):
            targetPath = msg_split[2].split("/")

    if(topic == "/movement"):
        if(state == States.followingPath and msg_split[1] == movementMachine and msg_split[0] == agentName):
            if(msg_split[2] == "BGN"):
                movementStarted = True
            if(msg_split[2] == "END"):
                movementFinished = True
    
    if(topic == "/confirmation"):
        if(state == States.atMachine and msg_split[0] == currentNode and msg_split[1] == agentName):
            taskDone = True



    



            
#MQTT setup
partAgent = smartServer.smartMqtt(agentName)
partAgent.client.subscribe("/partBids")
partAgent.client.subscribe("/machineBids")
partAgent.client.subscribe("/machining")
partAgent.client.subscribe("/partAgents")
partAgent.client.subscribe("/confirmation")
partAgent.client.subscribe("/pathRequests")
partAgent.client.subscribe("/movement")
partAgent.client.subscribe("/pathResponses")
partAgent.client.subscribe("/partAgentLogging")
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
                    movementMachine = targetPath[0]
                    state = States.followingPath
                    movementStarted = False
                    movementFinished = False
                    #Need to talk to jonathan about how this is gonna work
                    partAgent.client.publish("/movement",agentName + "," + movementMachine + "," + currentNode + "," + )

                    prevTime = time.time()
                    currentTime = prevTime

                    while(currentTime - prevTime < 5):
                        if(movementStarted):
                            break
                        currentTime = time.time()
                        partAgent.client.loop(0.1)

                    if(not movementStarted):
                        continue
                    else:
                        while(not movementFinished):
                            partAgent.client.loop(0.1)
                        currentNode = targetPath[0]
                        partAgent.client.publish("/partAgentLogging",agentName + "," + currentNode)
                       

            #Machine Agent stuff happens now - also account for if in buffer or at final output platform
            state = States.atMachine
            if("buffer" in currentNode): #Look into buffer naming
                reset()
            elif("output" in currentNode): #If you end up in an output node
                taskDone = True
            else:
                partAgent.client.publish("/machining",agentName + "," + currentNode + "," + currentTask)
                while(not taskDone):
                    partAgent.client.loop(0.1)








    




            
            


        




    

    

 




            




                






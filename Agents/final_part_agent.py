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
agentName = str(sys.argv[1])
taskList = sys.argv[2].split("-")
currentTask = ""
taskDone = False
machineList = []
currentTime = 0
prevTime = 0
score = float(sys.argv[3])
state = ""
targetPath = []
currentNode = "LINEAR_CONVEYOR"
nextNode = ""
targetNode = ""
movementMachine = ""
movementStarted = False
movementFinished = False
partStartedMovingFlag = False

print(taskList)
print(score)
print(agentName)


def reset():
    global currentTask
    global taskDone
    global machineList
    global state
    global targetPath
    global movementMachine
    global movementStarted
    global movementFinished
    global nextNode

    currentTask = ""
    taskDone = False
    machineList = []
    state = ""
    targetPath = []
    movementMachine = ""
    movementStarted = False
    movementFinished = False
    nextNode = ""



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
            if(msg_split[2] == agentName and msg_split[0] != currentNode):
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
partAgent.client.subscribe("/cancellation")
partAgent.client.subscribe("/partBooked")
partAgent.client.subscribe("/debug")
partAgent.client.on_message = msg_func

#Jono addition: when part agent first initialises, print its location
partAgent.client.publish("/partAgentLogging",partAgent.name + "," + currentNode)


while (len(taskList) != 0):
    partAgent.client.loop(0.1)

    currentTask = taskList[0]

    if(taskDone):
        print("Task done, removing from list")
        taskList.pop(0) #Remove the first task in the list
        taskDone = False
        reset()
    
    else:
        if(len(machineList) == 0):
        #Creating auction
            print("Starting auction for machines")
            state = States.acceptingBids
            partAgent.client.publish("/partBids",agentName + "," + str(score) + "," + currentTask)
            currentTime = time.time()
            prevTime = currentTime
            while(currentTime - prevTime < 2): # Wait time needs to be double the machine time?
                partAgent.client.loop(0.1)
                currentTime = time.time()
        
        else:
            #Sends confirmation to chosen machine
            #------------------------------------------------------------------------
            print("Machine chosen, going to machine now...")
            machineList.sort(key = lambda x:x[1])
            partAgent.client.publish("/debug",agentName + ":  " + str(machineList))
            state = States.findingPath #Doesn't matter what this is.
            chosenMachine = machineList[0]  #Based on machining time    
            partAgent.client.publish("/confirmation",agentName + "," + chosenMachine[0] + "," +  "You are chosen")
            #--------------------------------------------------------------------------------


            #Start to follow path to target node (chosen Machine)
            #-----------------------------------------------------------------------------------
            targetNode = chosenMachine[0]
            while(currentNode != targetNode):
                targetPath = []
                partAgent.client.publish("/pathRequests",agentName + "," + currentNode + "," + targetNode)
                while(len(targetPath) == 0): #Waits till a response is recieved from the graph agent
                    partAgent.client.loop(0.1)

                if(targetPath[0] == "no path exists"):
                    reset()
                    print("No path found, going to auction again :(")
                    partAgent.client.publish("/cancellation",agentName+ "," + chosenMachine[0])
                    break
                else:
                    print("path exists")
                    movementMachine = targetPath[-1]
                    nextNode = targetPath[1]
                    state = States.followingPath
                    movementStarted = False
                    movementFinished = False

                    partAgent.client.publish("/movement",agentName + "," + movementMachine + "," + currentNode + "," + nextNode)

                    prevTime = time.time()
                    currentTime = prevTime

                    while(currentTime - prevTime < 3):
                        if(movementStarted):
                            if(partStartedMovingFlag == False):
                                partAgent.client.publish("/partBooked","Motion Started")
                                partStartedMovingFlag = True
                            break
                        currentTime = time.time()
                        partAgent.client.loop(0.1)

                    if(not movementStarted):
                        state = States.findingPath
                        continue
                    else:
                        while(not movementFinished):
                            partAgent.client.loop(0.1)
                        currentNode = nextNode
                        partAgent.client.publish("/partAgentLogging",agentName + "," + currentNode)
                    state = States.findingPath
                       


            if(state == States.findingPath):
                #Machine Agent stuff happens now - also account for if in buffer or at final output platform
                state = States.atMachine
                if("BUFFER" in currentNode): #Look into buffer naming
                    reset()
                elif("EXIT" in currentNode): #If you end up in an output node
                    taskDone = True
                else:
                    partAgent.client.publish("/machining",agentName + "," + currentNode + "," + currentTask)
                    while(not taskDone):
                        partAgent.client.loop(0.1)


partAgent.client.publish("/partAgentLogging",partAgent.name + ",END")
prevTime = time.time()
while(time.time() - prevTime < 2):
    partAgent.client.loop(0.1)






    




            
            


        




    

    

 




            




                






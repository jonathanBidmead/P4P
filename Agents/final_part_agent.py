import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
from opcua import uamethod
import asyncio
import time

#OPCUA stuff to be implemented later. Refer to Lathe1.py for implementing OPCUA stuff

#Variables and Flags
agentName = "Agent 1"
taskList = ["task1","task2"]
currentTask = "nothing"
taskDone = False
machineList = []
currentTime = 0
prevTime = 0




def msg_func(client,userdata,msg):


    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)
    topic = msg.topic
    msg_split = msg_decoded.split("/")



        

            
#MQTT setup
partAgent = smartServer.smartMqtt(agentName)
partAgent.client.subscribe("/partBids")
partAgent.client.subscribe("/machineBids")
partAgent.client.subscribe("/machining")
partAgent.client.subscribe("/partAgents")
partAgent.client.on_message = msg_func

while len(taskList != 0):
    partAgent.client.loop(0.1)

    currentTask = taskList[0]

    if(taskDone):
        taskList.pop(0) #Remove the first task in the list
        taskDone = False
    
    else:
        if(len(machineList) == 0):
        #Creating auction
            partAgent.client.publish("/partBids","/everyone",currentTask)
            currentTime = time.time()
            prevTime = currentTime
            while(currentTime - prevTime < 5):
                partAgent.client.loop(0.1)
                currentTime = time.time()
        
        else:
            chosenMachine = machineList[0]  #Based on machining time?
            partAgent.client.publish("/partBids",chosenMachine + "You are chosen")

            partAgent.client.publish("/graphserver","share path to" + chosenMachine)
            


        




    

    

 




            




                






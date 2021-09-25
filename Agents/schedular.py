import os
import subprocess
import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
import time


#Initial variables
agentNumber = 1
order_list = [] #List of functions,quantity,time deadline (in minutes)
task_list = []
quantity = 0
agentsInitialised = 0


def msg_func(client,userdata,msg):
    global task_list
    global quantity
    global agentNumber
    global agentsInitialised

    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)

    if(msg.topic == "/schedular"):
        msg_split = msg_decoded.split(",")
        task_list = msg_split[0]
        quantity = msg_split[1]

        for i in range(0,int(quantity)):
            order_list.append(("AGENT_" + str(agentNumber),task_list,msg_split[2]))
            agentNumber += 1
            order_list.sort(key=lambda x:x[2])
    
    if(msg.topic == "/partBooked"):
        agentsInitialised -= 1




agentName = "SCHEDULAR"
agent = smartServer.smartMqtt(agentName)
agent.client.subscribe("/schedular")
agent.client.subscribe("/partBooked")
agent.client.on_message = msg_func


currentTime = 0
prevTime = 0

while True:
    agent.client.loop(0.1)
    
    while(agentsInitialised < 3 and len(order_list) !=0 ):
        subprocess.Popen('schedular.sh %s %s %s' %(order_list[0][0],order_list[0][1],order_list[0][2]), shell = True)
        order_list.pop(0)
        agentsInitialised += 1

    currentTime = time.time()
    if(currentTime - prevTime > 3):
        print(order_list)
        prevTime = currentTime









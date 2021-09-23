import os
import subprocess
import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer


flag = False

def msg_func(client,userdata,msg):
    global flag

    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)
    flag = True
    

    




agentName = "HMI"
agent = smartServer.smartMqtt(agentName)
agent.client.subscribe("/schedular")
agent.client.on_message = msg_func


while True:
    user_input = input("What part would you like to order: ")
    agent.client.publish("/schedular",user_input)
    while(not flag):
        agent.client.loop(2)
    flag = False





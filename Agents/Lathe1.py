import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
from MultiAgent import smartServer
from opcua import uamethod
import asyncio
import time

url = "localhost"
port = 4002
end_point = "opc.tcp://{}:{}".format(url, port)

latheOpcua = smartServer.smartOpcua(url,port,'Lathe1','server')

busy = False

@uamethod
def request(parent,function):
    global busy
    if(function == "Available"):
        return not busy

    elif(not busy):
        if(function == "Open Door"):
            doorOpen()
        elif(function == "Close Door"):
            doorClose()
        elif(function == "Thread"):
            threading()
        elif(function == "Chamfer"):
            chamfer()
        busy = True
        print(function + " completed")
        busy = False
        return True
    return False

def doorOpen():
    print("Doors open")
    time.sleep(2)

def doorClose():
    print("Doors closed")
    time.sleep(2)

def threading():
    print("Threading started.....")
    time.sleep(2)

def chamfer():
    print("Chamfering started")
    time.sleep(2)

latheOpcua.addMethods([request],['request'])

try:
    latheOpcua.server.start()
except Exception as e:
    print(e)
    



#msgs
msg_auctions = []
msg_publish = []
#Message format:
# /agentName


def msg_func(client,userdata,msg):
    msg_decoded = msg.payload.decode("utf-8")
    print("Received message: " + msg.topic + " -> " + msg_decoded)
    
    msg_split = msg_decoded.split("/")
    requestedTask = msg_split[1]
    

    if(msg.topic == "/auction"):
        for func in functions:
            if(requestedTask == func):
                latheAgent.client.publish("/bids","lathe1/yes!")
                break
            

    


latheAgent = smartServer.smartMqtt("lathe1")
latheAgent.client.subscribe("/auction")
latheAgent.client.subscribe("/bids")
latheAgent.client.on_message = msg_func

#Flags
published = False

#Tasks
functions = ["lathe"]

waitTime = 5
currTime = 0
prevTime = 0

while True:
    latheAgent.client.loop(0.1)
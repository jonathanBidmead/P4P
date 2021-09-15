import sys
from urllib.request import DataHandler
#mqtt imports and stuff
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')
from MultiAgent import smartServer
import asyncio
import time
import datetime

#opcua imports and stuff
from opcua import Client
url = "localhost"
port = 7002
name = "MOVEMENT_AGENT_CLIENT"
end_point = "opc.tcp://{}:{}".format(url, port)
opcClient = smartServer.smartOpcua(url,port,name,"client")
opcClient.client.connect()
method = opcClient.methods
print(method)
#internal variables for when this agent is in use
busy = method[2].get_data_value().Value.Value
currentlyMoving = False
currentPartAgent = ""
#getting the method for actually moving from the node
startMoveBetweenNodes = method[3]

#DEBUG: testing a more robust way of getting methods and variables from the objects node
# methodsList = []
# variablesList = []
# for i in method:
#     tempClass = i.get_node_class()
#     if(str(tempClass) == "NodeClass.Method"):
#         methodsList.append(str(i.get_browse_name())[16:-1])
#     if(str(tempClass) == "NodeClass.Variable"):
#         variablesList.append(i.get_data_value())
#         print(i.get_data_value().Value.Value)#returns the actual value stored in the variable
#         print(i.get_browse_name())#returns the name of the variable
# print(methodsList)
# print(variablesList)




#things to change when making different movement agents
name = "MOVEMENT_AGENT_TEST"
guiLocation = "0 0"
initialAdjacents = "NODE2,NODE1"

#creating server instance
movementAgent = smartServer.smartMqtt(name)

#internal variable for when this agent is in use
# busy = False

#creating/subscribing to pertinent mqtt topics
movementAgent.client.subscribe("/activeResources")
movementAgent.client.subscribe("/movement")
movementAgent.client.subscribe("/keepAlivePings")

#send initialisation to central graph server
movementAgent.client.publish("/activeResources","ADD," + movementAgent.name + ",MOVEMENT," + guiLocation + "," + initialAdjacents)

def msg_func(client,userdata,msg):
    msg_decoded = msg.payload.decode("utf-8")

    #pinging response (copy paste this to other servers)
    if(msg.topic == "/keepAlivePings"):
        if(msg_decoded == "PING"):
            agent = movementAgent#replace with current agent
            agent.client.publish("/keepAlivePings",agent.name)
    
    if(msg.topic == "/movement"):
        tempData = msg_decoded.split(",")
        adjacentList = initialAdjacents.split(",")
        if(tempData[1] in adjacentList and tempData[2] in adjacentList and not busy):#if part agent current node and target node both adjacent to this movement agent & this agent isn't currently busy
            movementAgent.client.publish("/movement",tempData[0] + "," + movementAgent.name + "," + "BGN")
            global currentPartAgent
            currentPartAgent = tempData[0]
            startMovement(tempData[1],tempData[2])

#communicating with the opcua layer
def startMovement(startNode,targetNode):
    print(opcClient.objects.call_method(startMoveBetweenNodes,startNode,targetNode))
    return(opcClient.objects.call_method(startMoveBetweenNodes,startNode,targetNode))
    



#defining msg_func (shortening variable names)
movementAgent.client.on_message = msg_func

while True:
    movementAgent.client.loop(0.1)

    busy = method[2].get_data_value().Value.Value

    if(busy and not currentlyMoving):
        currentlyMoving = True

    if(not busy and currentlyMoving):
        movementAgent.client.publish("/movement",currentPartAgent + "," + movementAgent.name + ",END")
        currentPartAgent = ""
        currentlyMoving = False
        print("Finished Motion")


    #DEBUG
    # time.sleep(2)
    # print("sending command")
    # #internal variable for when this agent is in use
    # busy = method[2].get_data_value().Value.Value
    # print("busy: " + str(busy))
    # if (busy == False):
    #     print(startMovement("llt","POR"))

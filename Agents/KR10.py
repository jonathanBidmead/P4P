# from Agents.OPCUA_SERVERS.test_movement_server import move
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
port = 7003
name = "KR10_CLIENT"
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
name = "KR10"
guiLocation = "5 2"
initialAdjacents = "CIRCULAR_CONVEYOR LATHE_1 LATHE_3 EXIT_PLATFORM_1"

#creating server instance
movementAgent = smartServer.smartMqtt(name)

#internal variables for start and end resources of this movement
startAgent = ""
endAgent = ""

#internal variable to stop fuckups with multiple transport agents
iPublishedThis = False
endMoveFull = False

#creating/subscribing to pertinent mqtt topics
movementAgent.client.subscribe("/activeResources")
movementAgent.client.subscribe("/movement")
movementAgent.client.subscribe("/keepAlivePings")
movementAgent.client.subscribe("/isResourceAvailable")

#send initialisation to central graph server
movementAgent.client.publish("/activeResources","ADD," + movementAgent.name + ",TRANSPORT," + guiLocation + "," + initialAdjacents)
initialAdjacents = initialAdjacents + " " + name
def msg_func(client,userdata,msg):
    global startAgent
    global endAgent
    global iPublishedThis
    global currentPartAgent
    msg_decoded = msg.payload.decode("utf-8")

    #pinging response (copy paste this to other servers)
    if(msg.topic == "/keepAlivePings"):
        if(msg_decoded == "PING"):
            agent = movementAgent#replace with current agent
            agent.client.publish("/keepAlivePings",agent.name)
    
    if(msg.topic == "/movement"):
        tempData = msg_decoded.split(",")
        if(tempData[1] == movementAgent.name and tempData[2] != "BGN" and tempData[2] != "END"):#only respond if the part agent requested this agent specifically
            adjacentList = initialAdjacents.split(" ")
            startAgent = tempData[2]
            endAgent = tempData[3]
            if(startAgent in adjacentList and endAgent in adjacentList and not busy):#if part agent current node and target node both adjacent to this movement agent & this agent isn't currently busy
                
                if(endMoveFull and currentPartAgent != tempData[0]):#if the previous move left the transport agent holding a part, only accept new requests from that part's agent 
                    pass
                else:
                    currentPartAgent = tempData[0]
                    
                    iPublishedThis = True
                    #checking if the first resource agent is available currently
                    if(startAgent == movementAgent.name):
                        movementAgent.client.publish("/isResourceAvailable",endAgent)
                    if(endAgent == movementAgent.name):
                        movementAgent.client.publish("/isResourceAvailable",startAgent)

            else:# if the movement was not accepted, clear these variables
                startAgent = ""
                endAgent = ""

    if(msg.topic == "/isResourceAvailable"):
        # global iPublishedThis
        tempData = msg_decoded.split(",")
        #
        if(len(tempData) == 2 and iPublishedThis == True):
            if(len(tempData) == 2 and tempData[0] == startAgent and tempData[0] != movementAgent.name):
                movementAgent.client.publish("/movement",currentPartAgent + "," + movementAgent.name + "," + "BGN")
                startMovement(startAgent,endAgent)
            if(len(tempData) == 2 and tempData[0] == endAgent and tempData[0] != movementAgent.name):
                movementAgent.client.publish("/movement",currentPartAgent + "," + movementAgent.name + "," + "BGN")
                startMovement(startAgent,endAgent)
            if(tempData == movementAgent.name):
                movementAgent.client.publish("/isResourceActive",movementAgent.name + ",YES")

#communicating with the opcua layer
def startMovement(startNode,targetNode):
    global iPublishedThis
    global endMoveFull
    iPublishedThis = False
    
    if (targetNode == movementAgent.name):
        endMoveFull = True
    else:
        endMoveFull = False
    print(opcClient.objects.call_method(startMoveBetweenNodes,startNode,targetNode))
    return(opcClient.objects.call_method(startMoveBetweenNodes,startNode,targetNode))
    



#defining msg_func (shortening variable names)
movementAgent.client.on_message = msg_func

while True:
    movementAgent.client.loop(0.1)

    busy = method[2].get_data_value().Value.Value


    #movement completed
    if(not busy and currentlyMoving ):
        movementAgent.client.publish("/movement",currentPartAgent + "," + movementAgent.name + ",END")
        # currentPartAgent = ""
        currentlyMoving = False
        print("Finished Motion")

    if(busy and not currentlyMoving):
        currentlyMoving = True

    #DEBUG
    # time.sleep(2)
    # print("sending command")
    # #internal variable for when this agent is in use
    # busy = method[2].get_data_value().Value.Value
    # print("busy: " + str(busy))
    # if (busy == False):
    #     print(startMovement("llt","POR"))

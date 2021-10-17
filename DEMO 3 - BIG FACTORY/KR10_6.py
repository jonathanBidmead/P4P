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
port = 7008
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

#things to change when making different movement agents
name = "KR10_6"
guiLocation = "-3 -3.5"
initialAdjacents = "PLATFORM_5 MILL_4 BUFFER_2"

#creating server instance
movementAgent = smartServer.smartMqtt(name)

#internal variables for start and end resources of this movement
startAgent = ""
endAgent = ""

#internal variable to stop fuckups with multiple transport agents
iPublishedThis = False
endMoveFull = False

#timeout variable
publishTime = 0

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
    global publishTime
    msg_decoded = msg.payload.decode("utf-8")

    #pinging response (copy paste this to other servers)
    if(msg.topic == "/keepAlivePings"):
        if(msg_decoded == "PING"):
            agent = movementAgent#replace with current agent
            agent.client.publish("/keepAlivePings",agent.name)
    
    if(msg.topic == "/movement"):
        tempData = msg_decoded.split(",")
        if(endMoveFull and currentPartAgent != tempData[0]):#if the previous move left the transport agent holding a part, only accept new requests from that part's agent 
            print ("skipped request from: " + tempData[0])
            pass
        elif(tempData[1] == movementAgent.name and tempData[2] != "BGN" and tempData[2] != "END" and not busy):#only respond if the part agent requested this agent specifically
            adjacentList = initialAdjacents.split(" ")
            startAgent = tempData[2]
            endAgent = tempData[3]
            print("this transport agent has been requested")
            if(startAgent in adjacentList and endAgent in adjacentList and not busy):#if part agent current node and target node both adjacent to this movement agent & this agent isn't currently busy
                print("not busy")
                #"busy" variable not updating fast enough leading to multiple requests reaching this point and overwriting eachother
            
                currentPartAgent = tempData[0]
                print("accepted movement")
                movementAgent.client.publish("/movement",currentPartAgent + "," + movementAgent.name + "," + "BGN")
                iPublishedThis = True
                publishTime = time.time()
                #checking if the first resource agent is available currently
                if(startAgent == movementAgent.name):
                    movementAgent.client.publish("/isResourceAvailable",endAgent)
                if(endAgent == movementAgent.name):
                    movementAgent.client.publish("/isResourceAvailable",startAgent)

            else:# if the movement was not accepted, clear these variables
                startAgent = ""
                endAgent = ""
                print("resetting nodes")

    if(msg.topic == "/isResourceAvailable"):
        # global iPublishedThis
        tempData = msg_decoded.split(",")
        #
        if(len(tempData) == 2 and iPublishedThis == True):
            if(len(tempData) == 2 and tempData[0] == startAgent and tempData[0] != movementAgent.name):
                # movementAgent.client.publish("/movement",currentPartAgent + "," + movementAgent.name + "," + "BGN")
                startMovement(startAgent,endAgent)
            if(len(tempData) == 2 and tempData[0] == endAgent and tempData[0] != movementAgent.name):
                # movementAgent.client.publish("/movement",currentPartAgent + "," + movementAgent.name + "," + "BGN")
                startMovement(startAgent,endAgent)
            if(tempData == movementAgent.name):
                movementAgent.client.publish("/isResourceActive",movementAgent.name + ",YES")

#communicating with the opcua layer
def startMovement(startNode,targetNode):
    global iPublishedThis
    global endMoveFull
    global currentPartAgent
    iPublishedThis = False
    
    if (targetNode == movementAgent.name):
        endMoveFull = True
        print("Just began a movement ending with me holding " + currentPartAgent)
    else:
        endMoveFull = False
        print("Just began a movement releasing " +  currentPartAgent)
    doofus = opcClient.objects.call_method(startMoveBetweenNodes,startNode,targetNode)
    print(doofus)
    return doofus
    



#defining msg_func (shortening variable names)
movementAgent.client.on_message = msg_func

while True:
    movementAgent.client.loop(0.5)

    busy = method[2].get_data_value().Value.Value
    if (iPublishedThis):
        busy = True

    if(iPublishedThis and time.time() - publishTime > 5):
        iPublishedThis = False
        busy = False
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

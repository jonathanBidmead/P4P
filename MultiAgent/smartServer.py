import opcua
from time import sleep
import paho.mqtt.client as mqtt
import asyncio



class smartOpcua:
    def __init__(self,url,port,name,type):
        if(type == "server"):
            endpoint = "opc.tcp://{}:{}".format(url,port)
            self.myserver = opcua.Server()
            self.myserver.set_endpoint(endpoint)
            self.addspace = self.myserver.register_namespace(name)
            self.objects = self.myserver.get_objects_node()
            self.param = self.objects.add_object(self.addspace,"parameters")
            self.type = type
        else:
            #implementatoin for opcua client
            pass

    def addMethods(self,methods,browsenames):
        for i in range(len(methods)):
            self.objects.add_method(1,browsenames[i],methods[i])
        return

class smartMqtt:
    def  __init__(self,name):
        self.msgs = []
        self.connectFlag = False
        self.client = mqtt.Client(name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        # enable TLS
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

        # set username and password
        self.client.username_pw_set("sahilbhatiani28@gmail.com", "v6SdZbjKzVvmX2b")

        # connect to HiveMQ Cloud on port 8883
        self.client.connect("0f6e8bd5af354092825491bb09ee56da.s1.eu.hivemq.cloud", 8883)


        while self.connectFlag != True:
            self.client.loop(0.1)

    
    def on_connect(self,client, userdata, flags, rc):
        self.connectFlag = True
        if rc == 0:
            print("Connected successfully")
        else:
            print("Connect returned result code: " + str(rc))

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self,client, userdata, msg):
        print("Received message: " + msg.topic + " -> " + msg.payload.decode("utf-8"))
        self.msgs.append(msg.payload.decode("utf-8"))








            



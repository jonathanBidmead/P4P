from time import sleep
import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print("Connect returned result code: " + str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " -> " + msg.payload.decode("utf-8"))

# create the client
client = mqtt.Client("client1")
client.on_connect = on_connect
client.on_message = on_message

# enable TLS
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

# set username and password
client.username_pw_set("sahilbhatiani28@gmail.com", "v6SdZbjKzVvmX2b")

# connect to HiveMQ Cloud on port 8883
client.connect("0f6e8bd5af354092825491bb09ee56da.s1.eu.hivemq.cloud", 8883)

# subscribe to the topic "my/test/topic"
client.subscribe("/machineBids")

# publish "Hello" to the topic "my/test/topic"
while True:
    client.connect("0f6e8bd5af354092825491bb09ee56da.s1.eu.hivemq.cloud", 8883)
    client.loop(0.1)
    sleep(5)

    client.publish("/machineBids","Yo wassup")


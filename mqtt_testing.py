import paho.mqtt.client as mqtt #import the client1
# broker_address="192.168.1.184" 
broker_address="test.mosquitto.org" #use external broker
client = mqtt.Client("P1") #create new instance
client.connect(broker_address) #connect to broker
client.publish("jono/newData","OFF")#publish
print('sdfds')
import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')



from MultiAgent import smartServer




a = smartServer.smartMqtt("bob")
a.client.subscribe("/machineBids")

while True:
    a.client.publish("/machineBids","Hello world!")


import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')
sys.path.append(r'C:\Users\drago\OneDrive\Documents\GitHub\P4P')


from MultiAgent import smartServer




a = smartServer.smartMqtt("bob")
a.client.subscribe("/pathRequests")
a.client.subscribe("/pathResponses")

a.client.publish("/pathRequests","Agent1" + "," + "LATHE" + "," + "LINEAR_CONVEYOR")
a.client.publish("/movement","Agent1," + "KR16," + "LINEAR_CONVEYOR,KR16")

a.client.loop_forever()


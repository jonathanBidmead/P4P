import sys
sys.path.append(r'C:\Users\sahil\Documents\Part 4\Mecheng 700\Code Base\P4P')



from MultiAgent import smartServer




a = smartServer.smartMqtt("bob")
a.client.subscribe("/pathRequests")
a.client.subscribe("/pathResponses")

a.client.publish("/pathRequests","Agen1" + "," + "DUMMY_AGENT" + "," + "LINEAR_CONVEYER")


a.client.loop_forever()


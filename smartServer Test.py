from MultiAgent import smartServer
import asyncio
import time





b = smartServer.smartMqtt("client1")

a = time.time()
while (time.time() - a < 20):
    b.client.loop(0.1)



print(b.msgs)










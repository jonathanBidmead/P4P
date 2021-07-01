from py_openshowvar import openshowvar
import opcua
from opcua import uamethod
client = openshowvar('10.104.117.1',7000)

# myServer = opcua.Server()
# url = "localhost"  # Localhost
# port = 7001  # Port number

# endpoint = "opc.tcp://{}:{}".format(url, port)  # Assemble endpoint URL
# myServer.set_endpoint(endpoint)

# name = "700_Test_Namespace"

# # Register the name on OPC UA namespace
# addSpace = myServer.register_namespace(name)

# # Get reference to the Objects node of the OPC UA server
# objects = myServer.get_objects_node()

# # Create objects on the object node
# param = objects.add_object(addSpace, "parameters")




def getCurrentPos():
    pos_string = client.read('$POS_ACT', debug=False)
    pos_string = pos_string.decode("utf-8")
    pos_string = pos_string.replace(',','')
    pos = pos_string.split()

    # print(pos[2])
    # print(pos[4])
    # print(pos[6])
    # print(pos[8])
    # print(pos[10])
    # print(pos[12])
    return([float(pos[2]),float(pos[4]),float(pos[6]),float(pos[8]),float(pos[10]),float(pos[12])])

def moveDirect(point):
    initialPos = getCurrentPos()
    # print(initialPos)
    point_rel = [0,0,0,0,0,0]
    for p in range(6):
        point_rel[p] = point[p] - initialPos[p]
    print(point_rel) 
    pos_asString = "{{X {}, Y {}, Z {}, A {}, B {}, C {}}}".format(point_rel[0], point_rel[1], point_rel[2], point_rel[3], point_rel[4], point_rel[5])
    print(pos_asString)
    if (client.read('my_step').decode('utf-8') == 'FALSE'):
        debug_rite_var = client.write('my_inc',pos_asString,debug=False)
        debug_write_var = client.write('my_step','TRUE',debug=False)

pointA = [50,-700,1300,-130,90,-40]

moveDirect(pointA)

# testString = '1.2,'
# print(testString)
# print(testString.replace(',',''))




client.close()
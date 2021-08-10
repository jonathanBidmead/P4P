from py_openshowvar import openshowvar


# create instances of KVP Servers
KVP_client = openshowvar('10.104.117.1',7000)

#Returns the current position as read from the robot 
#Note: If "Tool" and "Base" are not set in the HMI/Teachpad, this method will fail and there is no error handling as yet,
def getCurrentPos_Internal():
    print("Inevitable Print from KVP Read")#openshowvar's .read() method always prints to the console, and I don't know of a way to disable it.
    #.read() returns a string of format something like "{E6POS: X 100, Y 200 ... }", these lines extract the relevant numbers
    
    pos_string = KVP_client.read('$POS_ACT')
    pos_string = pos_string.decode("utf-8")
    pos_string = pos_string.replace(',','')
    pos = pos_string.split()

    print("Current Pos From KVP")
    print(pos[2])
    print(pos[4])
    print(pos[6])
    print(pos[8])
    print(pos[10])
    print(pos[12])
    return([float(pos[2]),float(pos[4]),float(pos[6]),float(pos[8]),float(pos[10]),float(pos[12])])

point = getCurrentPos_Internal()
# pointA = [-70,-586,1278,90,0,180]
pointA = [-108,-682,1264,72,79,153]
point_rel = [0,0,0,0,0,0]
for i in range(len(point)):
    point_rel[i] = pointA[i]-point[i]

#only send a new point to the robot if it has finished the previous motion
if (KVP_client.read('my_step').decode('utf-8') == 'FALSE'):
    

    KVP_client.write('MYX',str(point_rel[0]))
    KVP_client.write('MYY',str(point_rel[1]))
    KVP_client.write('MYZ',str(point_rel[2]))
    KVP_client.write('MYA',str(point_rel[3]))
    KVP_client.write('MYB',str(point_rel[4]))
    KVP_client.write('MYC',str(point_rel[5]))
    KVP_client.write('MYE1',str(0))#TODO: Implement E1 Properly
    KVP_client.write('my_step','TRUE')
    print("Point Sent to Robot")

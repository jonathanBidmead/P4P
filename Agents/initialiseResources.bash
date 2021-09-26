#remember to start graph server before any of these seperately
python graph_server.py & 
sleep 1
python OPCUA_SERVERS/KR10_OPCUA.py & 
python OPCUA_SERVERS/KR16_OPCUA.py & 
python KR10.py & 
# python KR16.py & 
# KR16_PID=$!
python BUFFER_1.py & 
python EXIT_PLATFORM_1.py & 
python LINEAR_CONVEYOR.py & 
python CIRCULAR_CONVEYOR.py & 
python LATHE_1.py & 
# python LATHE_2.py & 
# L2_PID=$!
# python LATHE_3.py & 
# L3_PID=$!
# python OPCUA_SERVERS/test_movement_server.py & disown
# python movementAgentTemplate.py & disown
# python dummyAgent.py & disown
# python Machine_Agent.py & disown
python schedular.py & 
python logging_server.py & 
sleep 10
python OPCUA_SERVERS/KR16_2_OPCUA.py & 
python KR16_2.py & 

# late start
# sleep 50
# python LATHE_2.py & 
# killing stuff
sleep 100
# kill $L3_PID
# kill $L2_PID
# kill $KR16_PID
sleep 100
python LATHE_3.py &
python KR16.py &
python LATHE_2.py &
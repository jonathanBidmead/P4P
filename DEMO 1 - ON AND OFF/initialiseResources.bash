#remember to start graph server before any of these seperately
python graph_server.py & 
sleep 1
#transport
python OPCUA_SERVERS/KR10_OPCUA.py & 
python OPCUA_SERVERS/KR16_OPCUA.py & 
python KR10.py & 
python KR16.py & 
#buffer
python BUFFER_1.py & 
python EXIT_PLATFORM_1.py & 
python ENTRY_PLATFORM.py & 
python PLATFORM_1.py & 
#machine
python LATHE_1.py & 
python LATHE_2.py & 
L2_PID=$!
#parts & logging
python schedular.py & 
python logging_server.py & 
# sleep 10
# python OPCUA_SERVERS/KR16_2_OPCUA.py & 
# python KR16_2.py & 
#killing Lathe 2
sleep 500
kill $L2_PID
#reviving Lathe 2
sleep 500
python LATHE_2.py &
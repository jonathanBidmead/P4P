#remember to start graph server before any of these seperately
python graph_server.py & 
sleep 1
#transport
python OPCUA_SERVERS/KR10_OPCUA.py & 
python OPCUA_SERVERS/KR16_OPCUA.py & 
python KR10.py & 
python KR16.py & 
#buffer
python EXIT_PLATFORM_1.py & 
python ENTRY_PLATFORM.py & 
python BUFFER_1.py & 
#machine
python LATHE_1.py & 
python LATHE_2.py & 
python MILL_1.py & 
python MILL_2.py & 
#parts & logging
python schedular.py & 
python logging_server.py & 

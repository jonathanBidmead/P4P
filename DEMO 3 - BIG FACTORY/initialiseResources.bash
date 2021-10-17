#remember to start graph server before any of these seperately
python graph_server.py & 
sleep 1

#first production line
#transport
python OPCUA_SERVERS/KR10_1.py & 
python OPCUA_SERVERS/KR10_2.py & 
python OPCUA_SERVERS/KR10_3.py & 
python KR10_1.py & 
python KR10_2.py & 
python KR10_3.py & 
#buffer
python EXIT_PLATFORM_1.py & 
python ENTRY_PLATFORM.py & 
python BUFFER_1.py & 
python PLATFORM_1.py & 
python PLATFORM_2.py & 
#machine
python LATHE_1.py & 
python LATHE_2.py & 
python MILL_1.py & 
python MILL_2.py & 
python PRINTER_1.py & 
python PRINTER_2.py & 

#parts & logging
python schedular.py & 
python logging_server.py & 

sleep 420

#second line
#transport
python OPCUA_SERVERS/KR10_5.py & 
python OPCUA_SERVERS/KR10_6.py & 
python OPCUA_SERVERS/KR10_7.py & 
python KR10_5.py & 
python KR10_6.py & 
python KR10_7.py & 

#buffer
python BUFFER_2.py & 
python PLATFORM_5.py & 
python PLATFORM_6.py & 

#machine
python LATHE_4.py & 
python MILL_3.py & 
python MILL_4.py & 
python PRINTER_4.py & 

sleep 420

#third line
#transport
python OPCUA_SERVERS/KR10_4.py & 
python KR10_4.py & 
#buffer
python PLATFORM_3.py & 
python PLATFORM_4.py & 
#machine
python LATHE_3.py & 
python PRINTER_3.py & 




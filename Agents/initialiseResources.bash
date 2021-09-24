#remember to start graph server before any of these seperately

python OPCUA_SERVERS/KR10_OPCUA.py & disown
python OPCUA_SERVERS/KR16_OPCUA.py & disown
python KR10.py & disown
python KR16.py & disown
# python BUFFER_1.py & disown
python EXIT_PLATFORM_1.py & disown
python LINEAR_CONVEYOR.py & disown
python CIRCULAR_CONVEYOR.py & disown
python LATHE_1.py & disown
# python LATHE_2.py & disown
# python LATHE_3.py & disown
# python OPCUA_SERVERS/test_movement_server.py & disown
# python movementAgentTemplate.py & disown
# python dummyAgent.py & disown
# python Machine_Agent.py & disown
python schedular.py & disown
python logging_server.py & disown
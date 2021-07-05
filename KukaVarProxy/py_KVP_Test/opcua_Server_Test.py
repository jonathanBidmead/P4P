from opcua import Client
url = "localhost"
port = 7001
end_point = "opc.tcp://{}:{}".format(url, port)
opcClient = Client(end_point)


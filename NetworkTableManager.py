from networktables import NetworkTables
import multiprocessing
sd = None

def sendNetworkTableNumber(name, info):
    global sd
    sd.putNumber(name, info)

def sendNetworkTableNumberArray(name, info):
    global sd
    sd.putNumberArray(name, info)
def getTables():
    global sd
    NetworkTables.startClientTeam(2169)
    NetworkTables.initialize(server= "10.21.69.2")
    while not NetworkTables.isConnected():
        print(NetworkTables.isConnected())
    
    sd =  NetworkTables.getTable("SmartDashboard")

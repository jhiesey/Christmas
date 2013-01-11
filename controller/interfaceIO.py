import serial

def printHex(data):
    print(' '.join( [ "%02X" % ord( x ) for x in data ] ))

class InterfaceIO(object):
    def __init__(self, port, timeout):
        self.ser = serial.Serial(port=port, timeout=timeout)    
    
    def receiveBytes(self, nBytes):
        data = self.ser.read(nBytes)
        if len(data) > 0:
            print("In: ")
            printHex(data)
        return data
        
    def sendBytes(self, data):
        print("Out: ")
        printHex(data)
        self.ser.write(data)
        
        
        
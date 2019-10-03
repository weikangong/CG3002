import serial
import time
import socket
import sys
import threading
import time
import CircularBuffer

mutex = threading.Lock()

class ReceiveData(threading.Thread):
        def __init__(self, buffer, port, period, packetSize):
                threading.Thread.__init__(self)
                self.buffer = buffer
                self.port = port
                self.period = period
                self.packetSize = packetSize

        def run(self):
                self.readData()

         # Read data from arduino
         # Packet format: Packet ID, x1, y1, z1, x2, y2, z2, x3, y3, z3,
         # voltage, current, power, cumpower, checksum
        def readData(self):
                nextTime = time.time() + self.period
                if not self.buffer.isFull():
                        rcv = self.port.read(self.packetSize)
                        mutex.acquire()
                        self.buffer.put(rcv)
                        mutex.release()
                threading.Timer(nextTime - time.time(), self.readData).start()

                        #Handshaking, keep saying 'H' to Arduino unitl Arduion reply 'A'
                while(self.port.in_waiting == 0 or self.port.read() != 'A'):
                        print ('Try to connect to Arduino')     
                        self.port.write('S')
                        time.sleep(1)
                        self.port.write('A')
                        print ('Connected')

                        #init threads
                commThread = ReceiveData(self.buffer, self.port,  0.003)
                

        
class clientComms():
        def __init__(self):
                self.socket = []

        def main(self):
                try:
                        self.setUpComms()
                        self.connectToServer(self.socket[0], self.socket[1])
                        self.sendMessage("test message")       #change this to be input
                except KeyboardInterrupt:
                        sys.exit(1)

        def setUpComms(self):
                self.socket.append(sys.argv[1])
                self.socket.append(sys.argv[2])

        def connectToServer(self, host, port):
                print("attempting to connect to server")
                self.HOST = host #"192.168.43.203"
                self.PORT = int(port) #8080
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((self.HOST, self.PORT))
                print("connected to server "+self.HOST+", port: "+str(self.PORT))

        def sendMessage(self, text):
                try:
                        self.s.send(text)
                except any:
                        print(any)

class Raspberry():
        def __init__(self):
                self.threads = []
                self.buffer = CircularBuffer.CircularBuffer(30)

        def main(self):
                # Set up port connection
                self.port=serial.Serial("/dev/serial0", baudrate=115200)
                self.port.reset_input_buffer()
                self.port.reset_output_buffer()

                # Handshaking
                while(self.port.in_waiting == 0 or self.port.read() != 'A'):
                    print ('Try to connect to Arduino')
                    self.port.write('S')
                    time.sleep(1)
                self.port.write('A');
                print ('Connected')

                receiveDataThread = ReceiveData(self.buffer, self.port, 0.003, 120)
                self.threads.append(receiveDataThread)
                
                # Start threads
                for thread in self.threads:
                    # thread.daemon = True # Runs in background
                    thread.start()

if __name__ == '__main__':
        pi = Raspberry()
        pi.main()
        # client = clientComms()
        # client.main()

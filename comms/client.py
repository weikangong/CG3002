import serial
import time
import socket
import sys
import threading
import RingBuffer as RB

mutex = threading.Lock()

class Raspberry():
        def __init__(self):
                self.buffer = RB.RingBuffer(32)
                self.powerList = [0, 0, 0, 0]

        def main(self):
                try: 
                        #set up port connection
                        self.port=serial.Serial("/dev/serial0", baudrate=115200)
                        self.port.reset_input_buffer()
                        self.port.reset_output_buffer()

                        #Handshaking, keep saying 'H' to Arduino unitl Arduion reply 'A'
                        while(self.port.in_waiting == 0 or self.port.read() != 'A'):
                                print ('Try to connect to Arduino')     
                                self.port.write('S')
                                time.sleep(1)
                                self.port.write('A')
                                print ('Connected')

                        #init threads
                        commThread = ReceiveData(self.buffer, self.port,  0.003)
                
                except KeyboardInterrupt:
                        sys.exit(1)
        
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

class ReceiveData(threading.Thread):
	def __init__(self, buffer, port, period):
		threading.Thread.__init__(self)
		self.buffer = buffer
		self.port = port
		self.period = period

	def run(self):
		self.readData()


	def readData(self):
		#start to receive data from mega
		nextTime = time.time() + self.period
		if not self.buffer.isFull():
			rcv = self.port.read(16)
			mutex.acquire()
			self.buffer.append(rcv)
			mutex.release()
		threading.Timer(nextTime - time.time(), self.readData).start()

if __name__ == '__main__':
        pi = Raspberry()
        #pi.main()
        client = clientComms()
        client.main()
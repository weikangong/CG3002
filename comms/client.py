import serial
import time
import socket

class Raspberry():
        def __init__(self):
                self.socket = []
                self.powerList = [0, 0, 0, 0]

        def main(self):
                #set up port connection
                self.port=serial.Serial("/dev/serial0", baudrate=115200)
                self.port.reset_input_buffer()
                self.port.reset_output_buffer()

                #wei kang, i commented this out for testing only
                '''

                #Handshaking, keep saying 'H' to Arduino unitl Arduion reply 'A'
                while(self.port.in_waiting == 0 or self.port.read() != 'A'):
                    print ('Try to connect to Arduino')
                    self.port.write('S')
                    time.sleep(1)
                self.port.write('A');
                print ('Connected')

                '''

                try:
                        self.setUpComms()
                        self.connectToServer(self.socket[0], self.socket[1])
                except KeyboardInterrupt:
                        sys.exit(1)

        def setUpComms(self):
                print ("Enter ip address: ")
                self.socket.append(sys.argv[1])
                print ("Enter port number: ")
                self.socket.append(sys.argv[2])

        def connectToServer(self, host, port):
                print("attempting to connect to server")
                self.HOST = host #"192.168.43.203"
                self.PORT = int(port) #8080
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((self.HOST, self.PORT))
                print("connected")
                self.s.send("this is test, plz work")

#		self.voltage = 0 #list[len(list)-1][0]
#		self.current = 0 #list[len(list)-1][1]
#		self.power = 0  #self.voltage*self.current
#		self.cumpower=0 #cumpower


if __name__ == '__main__':
        pi = Raspberry()
        pi.main()
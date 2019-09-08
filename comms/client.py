import serial
import time
import socket

class Raspberry():
        def main(self):
                #set up port connection
                self.port=serial.Serial("/dev/serial0", baudrate=115200)
                self.port.reset_input_buffer()
                self.port.reset_output_buffer()

                #Handshaking, keep saying 'H' to Arduino unitl Arduion reply 'A'
                while(self.port.in_waiting == 0 or self.port.read() != 'A'):
                    print ('Try to connect to Arduino')
                    self.port.write('S')
                    time.sleep(1)
                self.port.write('A');
                print ('Connected')

        def connectToServer(self):
                print("attempting to connect to server")
                self.HOST = "192.168.1.175"
                self.PORT = 8080
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((self.HOST, self.port))
                print("connected")
                self.s.send("this is test, plz work")

#		self.voltage = 0 #list[len(list)-1][0]
#		self.current = 0 #list[len(list)-1][1]
#		self.power = 0  #self.voltage*self.current
#		self.cumpower=0 #cumpower


if __name__ == '__main__':
        pi = Raspberry()
        pi.main()
        pi.connectToServer()
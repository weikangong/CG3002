import serial
import time

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
        
if __name__ == '__main__':
        pi = Raspberry()
        pi.main()
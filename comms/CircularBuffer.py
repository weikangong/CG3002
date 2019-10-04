class CircularBuffer():
        def __init__(self, bufferSize):
                self.size = bufferSize
                self.buffer = [None]*bufferSize
                self.ackID = 0
                self.nextID = 0
                self.full = False

        def put(self, packet):
                result = [x.rstrip('\x00') for x in packet.split(',')]
                #print (result)
                print (self.nextID)
                print (str(int(result[0])))
                if self.nextID == int(result[0]):
                        if self.ackID == (self.nextID + 1) % self.size:
                                self.full = True
                                print("buffer full")
                        else:
                                self.buffer[self.nextID] = result
                                print ("buffer saving: "+str(self.buffer[self.nextID]))
                                self.nextID = (self.nextID + 1) % self.size

        # Returns list of packets ordered from old to new
        def get(self):
                if(self.ackID <= self.nextID):
                        print ("buffer get: "+str(self.buffer[self.ackID:self.nextID]))
                        return self.buffer[self.ackID:self.nextID]
                else:
                        print ("buffer get: "+str(self.buffer[self.ackID:self.size] + self.buffer[:self.nextID]))
                        return self.buffer[self.ackID:self.size] + self.buffer[:self.nextID]

        def ack(self, index):
                self.ackID = index
                self.full = False

        def nack(self, index):
                self.ackID = index;
                self.nextID = index; # Discard all of the frame after
                self.full = False

        def getSize(self):
                return self.size

        def isFull(self):
                return self.full

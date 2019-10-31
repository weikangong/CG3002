class CircularBuffer():
        def __init__(self, bufferSize):
            self.size = bufferSize
            self.buffer = [None]*bufferSize
            self.ackID = 0
            self.nextID = 0
            self.full = False

        def put(self, packet):
            result = [x.rstrip('\x00') for x in packet.split(',')]
            print("nextID: " + self.nextID + " " + int(result[0]))
            packetID = packet.split(',', 1)[0];
            print("packetID: " + packetID);
            if self.nextID == int(result[0]):
                if self.ackID == (self.nextID + 1) % self.size:
                    self.full = True
                else:
                    packet = packet.split("\n", 1)[0] # Remove garbage chars after newline
                    self.buffer[self.nextID] = packet
                    self.nextID = (self.nextID + 1) % self.size

        # Returns list of packets ordered from old to new
        def get(self):
            if(self.ackID <= self.nextID):
                return self.buffer[self.ackID:self.nextID]
            else:
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

class CircularBuffer():
		def __init__(self, bufferSize):
		    	self.size = bufferSize
				self.buffer = [None]*bufferSize
				self.ackID = 0
				self.nextID = 0
				self.isFull = False

	   	def put(self, packet):
				result = [x.strip() for x in packet.split(',')]
				if self.nextID == result[0]:
			 	        if self.ackID == (self.nextID + 1) % self.size:
								self.isFull = True
								print("buffer full")
			        	else:
								self.buffer[self.nextID] = result
								self.nextID = (self.nextID + 1) % self.size

		# Returns list of packets ordered from old to new
    	def get(self):
				if(self.ackID <= self.nextID):
		       			return self.buffer[self.ackID:self.nextID]
				else:
						return self.buffer[self.ackID:self.size] + self.buffer[:self.nextID]

	   	def ack(self, index):
				self.ackID = index
				self.isFull = False

    	def nack(self, index):
				self.ackID = index;
				self.nextID = index; # Discard all of the frame after
				self.isFull = False

		def getSize(self):
				return self.size

		def isFull(self):
				return self.isFull

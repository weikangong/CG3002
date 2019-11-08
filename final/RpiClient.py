import serial
import time
import socket
import sys
import os
import threading
import time
import CircularBuffer
import operator
import csv

from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util.py3compat import *

import base64
import numpy as np
import pandas as pd
from sklearn.externals import joblib
from scipy import stats
from sklearn import preprocessing

# Constant variables
mutex = threading.Lock()
packetSize = 150
sampleSize = 30
receiveDataPeriod = 0.003
storeDataPeriod = 0.03
machineLearningPeriod = 4
transitionPeriod = 0.5

class MachineLearning(threading.Thread):
    def __init__(self, client, datasetList, period, N):
        threading.Thread.__init__(self)
        self.client = client
        self.datasetList = datasetList
        self.period = period
        self.N = N
        self.model = joblib.load("/home/pi/Desktop/cg3002/software/RF4.pkl")

    def run(self):
        threading.Timer(self.period, self.runMachineLearning).start()

    def runMachineLearning(self):
        nextTime = time.time() + self.period
        currTime = time.time()
        print('datasetList size: ' + str(len(self.datasetList)))

        if len(self.datasetList) >= 120:
            mutex.acquire()
            dataset = pd.DataFrame(self.datasetList)
            mutex.release()

            dataset.columns =  ['x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'x3', 'y3', 'z3','x4', 'y4', 'z4']
            df_mean1 = dataset.groupby([np.arange(len(dataset.index)) // self.N], axis=0).mean()
            df_mean1.rename(
                columns={'x1': 'x1_mean', 'y1': 'y1_mean', 'z1': 'z1_mean', 'x2': 'x2_mean', 'y2': 'y2_mean',
                         'z2': 'z2_mean', 'x3': 'x3_mean', 'y3': 'y3_mean', 'z3': 'z3_mean', 'x4': 'x4_mean', 'y4': 'y4_mean', 'z4': 'z4_mean'}, inplace=True)

            df_max1 = dataset.groupby([np.arange(len(dataset.index)) // self.N], axis=0).max()
            df_max1.rename(columns={'x1': 'x1_max', 'y1': 'y1_max', 'z1': 'z1_max', 'x2': 'x2_max', 'y2': 'y2_max',
                                    'z2': 'z2_max',
                                    'x3': 'x3_max', 'y3': 'y3_max', 'z3': 'z3_max', 'x4': 'x4_max', 'y4': 'y4_max', 'z4': 'z4_max'}, inplace=True)

            df_var1 = dataset.groupby([np.arange(len(dataset.index)) // self.N], axis=0).var()
            df_var1.rename(columns={'x1': 'x1_var', 'y1': 'y1_var', 'z1': 'z1_var', 'x2': 'x2_var', 'y2': 'y2_var',
                                    'z2': 'z2_var',
                                    'x3': 'x3_var', 'y3': 'y3_var', 'z3': 'z3_var', 'x4': 'x4_var', 'y4': 'y4_var', 'z4': 'z4_var'}, inplace=True)

            df1 = df_mean1.join(df_max1)
            df1 = df1.join(df_var1)
            df = preprocessing.normalize(df1)

            result_arr = self.model.predict(df)
            result = stats.mode(self.model.predict(df))

            timeTaken = time.time() - currTime
            print('Time taken to predict: ' + str(timeTaken))
            print('Modes = ' + str(result_arr))

            if result[0][0] != 'idle':
                print('Result = ' + str(result[0][0]))
                self.client.prepareAndSendMessage(result[0][0])

                if result[0][0] == 'logout':
                    self.client.stopConnectionAndExit()
            else:
                print('Result = idle, not sending message')
            threading.Timer(transitionPeriod, self.resetDatasetList).start()
        threading.Timer(nextTime - time.time(), self.runMachineLearning).start()

    def resetDatasetList(self):
        self.datasetList[:] = []

class ReceiveData(threading.Thread):
    def __init__(self, buffer, port, period, packetSize):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.port = port
        self.period = period
        self.packetSize = packetSize

    def run(self):
        self.receiveData()

     # Read data from Arduino
     # Packet format: Packet ID, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4,
     # voltage, current, power, cumpower, checksum
    def receiveData(self):
        nextTime = time.time() + self.period
        if not self.buffer.isFull():
            rcv = self.port.read(self.packetSize)
            mutex.acquire()
            self.buffer.put(rcv)
            mutex.release()
        threading.Timer(nextTime - time.time(), self.receiveData).start()

class StoreData(threading.Thread):
    def __init__(self, buffer, port, client, datasetList, powerList, period):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.port = port
        self.client = client
        self.datasetList = datasetList
        self.powerList = powerList
        self.period = period
        self.nextID = 0
        self.printCSV = sys.argv[3].lower() == 'true'

    def run(self):
        self.storeData()

    def storeData(self):
        nextTime = time.time() + self.period
        mutex.acquire()
        bufferList = self.buffer.get()
        mutex.release()

        if bufferList:
            for packet in bufferList:
                checksum = int(packet.rsplit(',', 1)[1])
                packet = packet.rsplit(',', 1)[0]
                testsum = reduce(operator.xor, [ord(c) for c in packet]) # xor inclusive of delimiter ,
                ack = False

                if testsum == checksum:
                    ack = True
                    packet = [float(data) for data in packet.split(',')]

                    self.powerList[0] = packet[13]
                    self.powerList[1] = packet[14]
                    self.powerList[2] = packet[15]
                    self.powerList[3] = packet[16]

                    self.nextID = (int(packet[0]) + 1) % self.buffer.getSize()
                    mutex.acquire()
                    self.datasetList.append(packet[1:13])
                    mutex.release()

                    if self.printCSV:
                        with open('/home/pi/Desktop/data.csv', 'a+') as csvfile:
                            filewriter = csv.writer(csvfile, delimiter = ',', quoting = csv.QUOTE_NONE)
                            filewriter.writerow(packet[1:13])
                else:
                    ack = False
                    print('Checksum failed')
                    break

            if ack:
                self.port.write('A')
                self.port.write(chr(self.nextID))
                mutex.acquire()
                self.buffer.ack(self.nextID)
                mutex.release()
            else:
                self.port.write('N')
                self.port.write(chr(self.nextID))
                mutex.acquire()
                self.buffer.nack(self.nextID)
                mutex.release()
        threading.Timer(nextTime - time.time(), self.storeData).start()

class ClientComms():
    def __init__(self, powerList, port):
        self.SECRET_KEY = 'panickerpanicker'
        self.HOST = sys.argv[1]
        self.PORT = int(sys.argv[2])
        self.powerList = powerList
        self.port = port
        self.connectToServer()

    def connectToServer(self):
        print('Attempting to connect to server')
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.HOST, self.PORT))
        print('Connected to server ' + self.HOST + ', port: ' + str(self.PORT))

    def stopConnectionAndExit(self):
        print("Logging out and exiting...")
        # Cleanup codes before exiting the program
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        self.port.write('R') # Resets the Arduino
        os._exit(0)

    def prepareAndSendMessage(self, action):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.SECRET_KEY, AES.MODE_CBC, iv)
        mutex.acquire()
        message = ('#' + action + '|' + str(self.powerList[0]) + '|' + str(self.powerList[1]) + '|' + str(self.powerList[2]) + '|' + str(self.powerList[3]) + '|').encode('utf8').strip()
        print('Sent message: ' + message)
        paddedMessage = self.padMessage(message, AES.block_size)
        encryptedMessage = cipher.encrypt(paddedMessage)
        encodedMessage = base64.b64encode(iv + encryptedMessage)
        self.sendMessage(encodedMessage)
        mutex.release()

    def padMessage(self, payload, block_size, style = 'pkcs7'):
        padding_len = block_size - len(payload) % block_size
        if style == 'pkcs7':
            padding = bchr(padding_len) * padding_len
        elif style == 'x923':
            padding = bchr(0) * (padding_len-1) + bchr(padding_len)
        elif style == 'iso786':
            padding = bchr(128) + bchr(0) * (padding_len - 1)
        else:
            raise ValueError('Unknown Padding Style')
        return payload + padding

    def sendMessage(self, text):
        try:
            self.s.send(text)
        except any:
            print()

class Raspberry():
    def __init__(self):
        self.threads = []
        self.buffer = CircularBuffer.CircularBuffer(sampleSize)
        self.client = []
        self.datasetList = []
        self.powerList = [0, 0, 0, 0]

    def main(self):
        if len(sys.argv) != 4:
            print('Invalid number of arguments')
            print('python RpiClient.py [IP address] [Port] [csv <True, False>]')
            sys.exit()

        try:
            # Initalize UART Port
            self.port = serial.Serial('/dev/serial0', baudrate = 115200)
            self.port.reset_input_buffer()
            self.port.reset_output_buffer()

            # Handshaking Protocol
            while(self.port.in_waiting == 0 or self.port.read() != 'A'):
                print ('Try to connect to Arduino')
                self.port.write('S')
                time.sleep(1)
            self.port.write('A')
            print ('Connected')

            # Client to Server Connection
            self.client = ClientComms(self.powerList, self.port)

            receiveDataThread = ReceiveData(self.buffer, self.port, receiveDataPeriod, packetSize)
            self.threads.append(receiveDataThread)

            storeDataThread = StoreData(self.buffer, self.port, self.client, self.datasetList, self.powerList, storeDataPeriod)
            self.threads.append(storeDataThread)

            MachineLearningThread = MachineLearning(self.client, self.datasetList, machineLearningPeriod, sampleSize)
            self.threads.append(MachineLearningThread)

            # Start threads
            for thread in self.threads:
                thread.daemon = True
                thread.start()

            # Prevents KeyboardInterrupt from being ignored
            while True:
                time.sleep(0.001)
        except KeyboardInterrupt:
            self.port.write('R') # Resets the Arduino
            print('Exiting...')
            sys.exit()

if __name__ == '__main__':
    pi = Raspberry()
    pi.main()

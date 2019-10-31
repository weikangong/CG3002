import serial
import time
import socket
import sys
import threading
import time
import CircularBuffer
import random
import operator
import csv

from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util.py3compat import *

import base64
import numpy as np
import pandas as pd
import math
import joblib
from scipy import stats
from sklearn import preprocessing

from RF import test_RF
from RF import train_RF

# Global variables
mutex = threading.Lock()

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

class MachineLearning(threading.Thread):
        def __init__(self, client, datasetList, period, N):
                threading.Thread.__init__(self)
                self.period = period
                self.datasetList = datasetList
                self.client = client
                self.rf = train_RF()
                self.N = N

        def run(self):
                self.run_machine_learning()

        def run_machine_learning(self):
                nextTime = time.time() + self.period
                #print(str(self.datasetList))
                if len(self.datasetList) >= 180:
                        #print(len(self.datasetList))
                        #print(str(self.datasetList))
                        dataset = pd.DataFrame(self.datasetList)
                        dataset = dataset.reset_index()
                        #print(dataset.head())
                        dataset = dataset.iloc[40:-10, 1:14]

                        #print(dataset.head())
                        dataset.columns =  ['index', 'x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'x3', 'y3', 'z3','x4', 'y4', 'z4']
                        dataset = dataset.astype('float32')
                        dataset = dataset.drop(columns=['index'])

                        #print("dataset: ")
                        #print(dataset)

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

                        df1 = df1.astype('float32')
                        df1 = df1.dropna()

                        df = preprocessing.normalize(df1)

                        result = test_RF(self.rf, df)

                        #print(str(len(dataset[0])))
                        #print("ml")
                        #model = joblib.load("/home/pi/Desktop/cg3002/comms/RF.pkl")

                        #result = stats.mode(model.predict(df1))

                        predicted_action = result

                        #once machine learning code is done, this function will send data

                        if result[0] != "idle" :
                                print(result[0])
                                self.client.prepareAndSendMessage(result[0])
                        else:
                                print("result = idle. not sending message")
                        #mutex.acquire()
                        self.datasetList[:] = []
                        #mutex.release()
                threading.Timer(6, self.run_machine_learning).start()

class StoreData(threading.Thread):
        def __init__(self, buffer, port, client, datasetList, powerList):
            threading.Thread.__init__(self)
            self.client = client
            self.buffer = buffer
            self.port = port
            self.powerList = powerList
            self.datasetList = datasetList

        def run(self):
            self.storeData()

        def storeData(self):
            mutex.acquire()
            bufferList = self.buffer.get()
            mutex.release()

            if bufferList:
                for packet in bufferList:
                    checksum = packet.rsplit(",", 1)[1]
                    packet = packet.rsplit(",", 1)[0]
                    testsum = reduce(operator.xor, [ord(c) for c in packet])
                    ack = False

                    if testsum == int(checksum):
                        ack = True
                        packet = packet.split(',')

                        self.powerList[0] = packet[13]
                        self.powerList[1] = packet[14]
                        self.powerList[2] = packet[15]
                        self.powerList[3] = packet[16]

                        self.nextID = (int(packet[0]) + 1) % self.buffer.getSize()

                        with open('/home/pi/Desktop/data.csv', 'a+') as csvfile:
                            filewriter = csv.writer(csvfile, delimiter = ',', quoting = csv.QUOTE_NONE)
                            filewriter.writerow(packet)
                        self.datasetList.append(packet)
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

            threading.Timer(0.06, self.storeData).start()


class ClientComms(threading.Thread):
        def __init__(self, powerList):
            threading.Thread.__init__(self)
            self.SECRET_KEY = "panickerpanicker"
            self.HOST = sys.argv[1]
            self.PORT = int(sys.argv[2])
            self.powerList = powerList
            self.connectToServer()

        def connectToServer(self):
            print("Attempting to connect to server")
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.HOST, self.PORT))
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.HOST, self.PORT))
            print("Connected to server " + self.HOST + ", port: " + str(self.PORT))

        def prepareAndSendMessage(self, action):
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(self.SECRET_KEY, AES.MODE_CBC, iv)
            mutex.acquire()
            message = ("#" + action + "|" + str(self.powerList[0]) + "|" + str(self.powerList[1]) + "|" + str(self.powerList[2]) + "|" + str(self.powerList[3]) + "|").encode('utf8').strip()
            print("sent message: " + message)
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
                raise ValueError("Unknown Padding Style")

            return payload + padding

        def sendMessage(self, text):
                try:
                    self.s.send(text)
                except any:
                    print()

class Raspberry():
        def __init__(self):
            self.threads = []
            self.buffer = CircularBuffer.CircularBuffer(30)
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
                    self.port = serial.Serial("/dev/serial0", baudrate = 115200)
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
                    self.client = ClientComms(self.powerList)

                    # Input: buffer, port, period, packet size
                    receiveDataThread = ReceiveData(self.buffer, self.port, 0.03, 150)
                    self.threads.append(receiveDataThread)

                    # Input: buffer, port, client, datasetList, powerList
                    storeDataThread = StoreData(self.buffer, self.port, self.client, self.datasetList, self.powerList)
                    self.threads.append(storeDataThread)

                    # Input: client, datasetList, period, dataset group size
                    MachineLearningThread = MachineLearning(self.client, self.datasetList, 5, 30)
                    self.threads.append(MachineLearningThread)

                    # Start threads
                    for thread in self.threads:
                        # thread.daemon = True # Runs in background
                        thread.start()

                except KeyboardInterrupt:
                    self.port.write('R') # Resets the Arduino
                    sys.exit(1)

if __name__ == '__main__':
        pi = Raspberry()
        pi.main()

## CG3002: Dance

Head over to our [Wiki Home][wiki] to find out on how to setup the dance prediction system. Below describes the various components of the system and their integration as a dance prediction system.

<p align="center">
  <img src="/images/main.jpg">
</p>

[wiki]:https://github.com/weikangong/CG3002/wiki

## Individual Components

### Hardware Folder

Important Files:
1. abc
2. def
3. jkl

### Communications Folder

Important Files:
1. ArduinoClient.ino - Responsible for implementation of FreeRTOS by Richard Barry to prioritise, schedule and execute the following tasks:
  * Reading data from sensor and power periodically
  * Parses and format the data to send in packet
  * Transmit data via wired UART connection to the Raspberry Pi
2. RpiClient.py - Responsible for setting up UART connection between Arduino Mega and Raspberry Pi, socket connection between the Raspberry Pi and the Server, and scheduling the following threads:
  * ReceiveData Thread: Receive packet from the Arduino Mega and store into Circular Buffer
  * StoreData Thread: Process data received in Circular Buffer correctness using checksum and store into list for MachineLearning thread
  * MachineLearning Thread: Predict move using the list and send it via secure, encrypted socket to the server
3. CircularBuffer.py - Implementation of array of size 30, the sample size needed for the prediction of a single dance move. Used by the ReceiveData thread to store the raw string packet received from the Arduino Mega immediately for later processing by the StoreData thread
4. RF.py - Model training for realtime training of model for dance prediction

### Software Folder

Important Files:
1. IndividualMoves.py (deprecated) - Segment training data into individual moves as training data contains multiple dance moves
2. SlidingWindow.py - Segment the training data in sliding windows of 50%. Also to aggregate extracted data
3. FeatureSelection.py - Select important/most correlated features to use for training/testing
4. Machine Learning Models (i.e. KNN.py, SVM.py, NN.py, RF.py) - Run models on Rpi, to generate and serialise model into Pickle file
5. Pickle Files (i.e. KNN.pkl, SVM.pkl, NN.pkl, RF.pkl) - Pre-trained machine learning model, loaded for prediction

## Integration

### Final Folder

Important Files:
1. ArduinoClient.ino - Same as in Communications Folder, with the integration and optimisation of reading sensor and power data from the Hardware Folder
2. RpiClient.py - Same as in Communication Folder, with the integration and optimisation of machine learning thread from the Software Folder
3. CircularBuffer - Same as in Communications Folder
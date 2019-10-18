# CG3002
This is the main repository for CG3002 project.

Steps to run server: run the code on ur laptop 

1. First run http-server on laptop. Example shown. Take note of ip address and port number

2. Then run:

sudo python [filepath]/final_eval_server_5moves.py [server ip address] [server port #] [group#]


Take note secret key : "panickerpanicker"
Also, dont worry about warning for secret key


Steps to run rpi+ arduino : 

1. Once rpi connected to screen or SSH, run the command:

sudo python Desktop/cg3002/comms/RpiClient.py [SERVER IP ADDRESS] [SERVER PORT #]

2. Remember to press reset button on arduino before every time u run code. Also if u keep getting the message "trying to connect", just restart arduino and try again for now. Theres a fix but it's hard to explain

3. The values all written to data.csv

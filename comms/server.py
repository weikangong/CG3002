import socket
print("hi")

ip_address = "192.168.137.9"    
port_number = 8080
    
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("socket created")
    
#initialize server 
server_address = (ip_address, port_number)
print('starting on '+ ip_address+ ' port: '+ str(port_number))
        
try:
    sock.bind(server_address)
except socket.error as msg:
    print(msg)
print("Socket bind complete.")

#Listen for connections

sock.listen(1)
connection, address = sock.accept()
print("connected to "+address[0] + ":" + str(address[1]))

data = connection.recv(1024)
print(data)
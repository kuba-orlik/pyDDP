import socket

HOST = 'localhost'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
text = '{"message":"Hello, World"}'
s.send(bytes(text, 'UTF-8'))
data = s.recv(1024)
s.close()
print('Received', repr(data))
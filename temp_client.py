import socket

HOST = 'localhost'    # The remote host
PORT = 50007              # bThe same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
text = '{"verb":"sub", "attributes":{"id":"dowolne_id","pub_name":"test"}}'
s.send(bytes(text, 'UTF-8'))
data = s.recv(1024)
s.close()
print('Received', repr(data))
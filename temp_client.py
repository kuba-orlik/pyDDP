import socket

HOST = 'localhost'    # The remote host
PORT = 50007              # bThe same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

text = '{"verb":"new_pub", "attributes":{"name":"test234","content":"{}"}}'
s.send(bytes(text, 'UTF-8'))
data = s.recv(1024)
print('Received', repr(data))

text = '{"verb":"delete_pub", "attributes":{"name":"test234"}}'
s.send(bytes(text, 'UTF-8'))
data = s.recv(1024)
print('Received', repr(data))

text = '{"verb":"new_pub", "attributes":{"name":"test234","content":"{\\\"title\\\":\\\"trololololo\\\"}"}}'
s.send(bytes(text, 'UTF-8'))
data = s.recv(1024)
print('Received', repr(data))

text = '{"verb":"update_pub", "attributes":{"pub_name":"test234","changes":[{"op": "add", "path": "/foo", "value": "bar"}]}}'
s.send(bytes(text, 'UTF-8'))
data = s.recv(1024)
print('Received', repr(data))

s.close()
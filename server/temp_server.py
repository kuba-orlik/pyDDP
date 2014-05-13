import time
import socket
import select
import threading
import sys
import os

from sys import path
path.append("classes/")

import client


HOST = '127.0.0.1'
#test
#HOST = input()

print ("Type port number");
PORT = int(input())


#create an INET, STREAMing socket
serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM) #SOCK_STREAM -> TCP
#bindowanie socketu na localhost:50007
serversocket.bind((HOST, PORT))
#ten socket defaultowo działa w sposób blokujący
#włącz nasłuchiwanie na socketcie serwerowym, (5) 0..5 maksymalna ilość socketów, które przyszły a nie dostały accept'a
serversocket.listen(5)

#tablica połączonych (aktualnie aktywnych) socketów, w tej tablicy przechowywujemy zaakceptowane sockety

#wywoływana w osobny wątku, w nieblokujący sposób zczytuje informacje od połączonych klientów
def monitorClients():
    while 1:
        time.sleep(0.2)
        #sprawdzenie czy są połączeni klienci
        if len(client.Collection.connected_sockets)>0:
            #zwraca liste odpowiednich socketów
            ready_to_read, ready_to_write, in_error = select.select(client.Collection.connected_sockets, [], [], 1)
            #pętla wykonuje się dla każdego socketu który jest gotowy do odczytu
            for socket in ready_to_read:
                client_temp = client.Collection.getBySocket(socket)
                error = False
                try:
                    data = socket.recv(1024)
                except ConnectionAbortedError:
                    error = True
                except ConnectionResetError:
                    error = True
                if error or len(data)==0:
                    client.Collection.connected_sockets.remove(socket)
                    print("client", client_temp.IDL, "disconnected")
                    client_temp.unsubAll()
                    continue
                client_temp.handleIncomingJSON(data)

client_monitor_thread = threading.Thread (target=monitorClients, args=() )
client_monitor_thread.start()

while 1:
    (client_socket, address) =  serversocket.accept()
    print("new client!")
    client_new = client.Client(client_socket, address)
    client.Collection.addClient(client_new)

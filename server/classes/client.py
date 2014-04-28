class Collection:
    #lista klientów (__init__ konstruktor) 
    clients=[]
    total_clients=0
    connected_sockets=[]

    #dodanie klienta do kolekcji
    def addClient(client):
        Collection.clients.append(client)
        client.IDL=Collection.total_clients
        Collection.total_clients+=1
        Collection.connected_sockets.append(client.socket)

    def getBySocket(socket):
        for client in Collection.clients:
            if client.socket==socket:
                return client
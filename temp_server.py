import socket
import select
import threading
import json

def prepareString(string):
    return bytes(string, "UTF-8")

#create an INET, STREAMing socket
serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('', 50007))
#serversocket.setblocking(0)
serversocket.listen(5)

connected_sockets=[]

def monitorClients():
    print(connected_sockets)
    while 1:
        if len(connected_sockets)>0:
            ready_to_read, ready_to_write, in_error = select.select(connected_sockets, [], [], 1)
            for socket in ready_to_read:
                client = clientCollection.getBySocket(socket)
                try:
                    data = socket.recv(1024)
                except ConnectionAbortedError:
                    connected_sockets.remove(socket)
                    print("client", client.id, "disconnected")
                    client.unsubAll()
                    continue
                client.parseIncomingJSON(data)
                client.respond(200, "ok", "ok")


class Publication():
    def __init__(self, ID):
        self.id=ID
        print(open('/pubs/test.pub'))
        self.name="publication_name_placeholder"

class PublicationCollection():
    def __init__(self):
        self
    def getPublicationByName(self, name):
        return name

class Subscription():
    def __init(self, client, publication):
        self.client = client
        self.publication = publication

class SubscriptionCollection():
    def __init__(self):
        self.subscriptions = []
        self.subscriptionsByPub = {}
    def indexSubByPub(self, sub):
        if not sub.publication.name in self.subscriptionsByPub:
            self.subscriptionsByPub[sub.publication.name]=[]
        self.subscriptionsByPub[sub.publication.name].append(sub)
    def getSubsByPubName(self, pub_name):
        return self.subscriptionsByPub[pub_name]
    def new(self, client, publication):
        sub = Subscription(client, publication)
        self.subscriptions.append(sub)
        self.subscriptionsByPub
        return sub
    def remove(self, sub):
        self.subscriptions.remove(sub)

class ClientCollection():
    def __init__(self):
        self.clients=[]
        self.total_clients=0
    def addClient(self, client):
        self.clients.append(client)
        client.id=self.total_clients
        self.total_clients+=1
        connected_sockets.append(client.socket)
    def getBySocket(self, socket):
        for client in self.clients:
            if client.socket==socket:
                return client

class Client():
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.id = None
        self.subscriptions = []
    def parseIncomingJSON(self, string):
        string = str(string, encoding='UTF-8')
        print(string)
        try:
            json_temp = json.loads(string)
            json_correct = True
        except ValueError:
            print("badly formatted json!")
            json_correct = False
        if json_correct:
            verb_present = 'verb' in json_temp
            print("verb_present:", verb_present)
            attributes_present = 'attributes' in json_temp
            if verb_present & attributes_present:
                self.do(verb, attributes)
    def do(self, verb, attrbiutes):
        if verb=="sub":
            pub = publicationCollection.getPublicationByName(attributes["name"])
            sub = subscriptionCollection.new(self, pub)
            self.subscriptions.append(sub)

    def respond(self, res_number, status, message):
            message = json.dumps({'res_number': res_number, 'status': status, 'message': message})
            self.socket.send(bytes(message, "UTF-8"))
    def unsubAll(self):
        for sub in self.subscriptions:
            self.subscriptions.remove(sub)
            subscriptionCollection.remove(sub)

client_monitor_thread = threading.Thread (target=monitorClients, args=() )
client_monitor_thread.start()

clientCollection = ClientCollection()
subscriptionCollection = SubscriptionCollection()
publicationCollection = PublicationCollection()

while 1:
    (new_clientSocket, address) =  serversocket.accept()
    client = Client(new_clientSocket, address)
    clientCollection.addClient(client)

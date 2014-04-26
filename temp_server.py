import socket
import select
import threading
import json

#parsowanie stringu na byte'y
def prepareString(string):
    return bytes(string, "UTF-8")

#create an INET, STREAMing socket
serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM) #SOCK_STREAM -> TCP
#bindowanie socketu na localhost:50007
serversocket.bind(('', 50007))
#ten socket jest defaultowo blokujący
#włącz nasłuchiwanie na socketcie serwerowym, (5) 0..5 maksymalna ilość socketów, które przyszły a nie dostały accept'a
serversocket.listen(5)

#tablica połączonych (aktualnie aktywnych) socketów, w tej tablicy przechowywujemy zaakceptowane sockety
connected_sockets=[]

#wywoływana w osobny wątku, w nieblokujący sposób zczytuje informacje od połączonych klientów
def monitorClients():
    while 1:
        #sprawdzenie czy są połączeni klienci
        if len(connected_sockets)>0:
            #zwraca liste odpowiednich socketów
            ready_to_read, ready_to_write, in_error = select.select(connected_sockets, [], [], 1)
            #pętla wykonuje się dla każdego socketu który jest gotowy do odczytu
            for socket in ready_to_read:

                client = clientCollection.getBySocket(socket)
                error = False
                try:
                    data = socket.recv(1024)
                except ConnectionAbortedError:
                    error = True
                if error or len(data)==0:
                    connected_sockets.remove(socket)
                    print("client", client.IDL, "disconnected")
                    client.unsubAll()
                    continue
                client.parseIncomingJSON(data)
                #client.respond(200, "ok", "ok")


class PubNotFoundError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PubDamagedError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BadJSONSyntaxError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Publication():
    def __init__(self, ID):
        self.IDL=ID
        self.file = open('pubs/'+ID+'.pub')
        #self.content = json.gets(self.file.read())
        self.content = self.file.read()
        try:
            self.parsed_content = json.loads(self.content)
        except Exception as e:
            raise BadJSONSyntaxError(e.value)
        self.name="publication_name_placeholder"
    def getContents(self):
        return self.content

class PublicationCollection():
    def __init__(self):
        self
    def getPublicationByName(self, name):
        try:
            pub= Publication(name)
        except BadJSONSyntaxError:
            print('publication content invalid')
            raise PubDamagedError("Publication content is not valid")
        except:
            raise PubNotFoundError("Publication not found")
        return pub

class Subscription():
    def __init__(self, client, publication, IDL):
        self.client = client
        self.publication = publication
        self.IDL=IDL

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
    def new(self, client, publication, idL):
        sub = Subscription(client, publication, idL)
        self.subscriptions.append(sub)
        self.subscriptionsByPub
        return sub
    def remove(self, sub):
        self.subscriptions.remove(sub)

#kolekcja klientów
class ClientCollection():
    #lista klientów (__init__ konstruktor) 
    def __init__(self):
        self.clients=[]
        self.total_clients=0
    #dodanie klienta do kolekcji
    def addClient(self, client):
        self.clients.append(client)
        client.IDL=self.total_clients
        self.total_clients+=1
        connected_sockets.append(client.socket)
    def getBySocket(self, socket):
        for client in self.clients:
            if client.socket==socket:
                return client

class Validator:
    def attributesPresent(needles, haystack):
        for needle in needles:
            if not needle in haystack:
                return False
        return True

class Client():
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.IDL = None
        self.subscriptions = []
    def parseIncomingJSON(self, string):
        #konwersja ciągu bajtów na stringa
        string = str(string, encoding='UTF-8')
        try:
            #parsowanie JSONa w postaci stringa na obiekt pythonowy (sprawdzenie poprawności sk)
            json_temp = json.loads(string)
            json_correct = True
        except ValueError:
            print("badly formatted json!")
            json_correct = False
        if json_correct:
            verb_present = 'verb' in json_temp
            print("verb_present:", verb_present)
            attributes_present = 'attributes' in json_temp
            print("attributes_present:", attributes_present)
            if verb_present & attributes_present:
                verb = json_temp["verb"]
                attributes = json_temp["attributes"]
                self.do(verb, attributes)
            else:
                self.reportBadSyntax()
    def reportBadSyntax(self):
        self.respond(300, "error", "bad request syntax")
    def hasSubID(self, IDL):
        for sub in self.subscriptions:
            if sub.IDL==IDL:
                return True
        return False
    def do(self, verb, attributes):
        if verb=="sub":
            self.__sub(attributes)
        else:
            print("bad verb")
            self.respond(300, "error", "unknown verb")



    def __sub(self, attributes):
        print("handling SUB request")
        if not Validator.attributesPresent(["id", "pub_name"], attributes):
            self.reportBadSyntax()
        hasSub = self.hasSubID(attributes["id"])
        print("hasSub:", hasSub)
        if hasSub:
            self.respond(422, "error", "you already have that id assigned to a publication. Unsub first")
            return
        try:
            pub = publicationCollection.getPublicationByName(attributes["pub_name"])
        except PubNotFoundError:
            self.respond(404, "error", "publication not found")
            return
        sub = subscriptionCollection.new(self, pub, attributes["id"])
        self.subscriptions.append(sub)
        print(self.subscriptions)
        self.respond(200, "ok", pub.getContents())


    def respond(self, res_number, status, message):
            message = json.dumps({'res_number': res_number, 'status': status, 'message': message})
            print("sending", message)
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

import socket
import select
import threading
import json
import sys
try:
    import jsonpatch
except:
    print("jsonpatch package has to be installed for this script to run properly. Install it and run this script again")
    sys.exit()
import os

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

    def applyPatch(self, patch):
        json_l = json.loads(self.content)
        print("before patch:", json_l)
        json_l = patch.apply(json_l)
        print("after patch: ", json_l)
        self.setContentByObject(json_l)

    def setContentByObject(self, object):
        self.content = json.dumps(object)
        self.setContentString(self.content)

    def __getFilePath(self):
        return "pubs/" + self.IDL + ".pub"

    def setContentString(self, string):
        f = open(self.__getFilePath(), "w")
        f.truncate()
        f.write(self.content)

    def propagate(self):
        clients = clientCollection.clients
        for client in clients:
            client.sendPubUpdate(self)

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

    def nameTaken(self, name):
        try:
            open("pubs/"+name+".pub")
        except FileNotFoundError:
            return False
        return True

    def createPublication(self, name, content):
        f = open("pubs/" + name + ".pub", "a")
        f.write(content)
        f.close()
        return Publication(name)

    def delete(self, name):
        os.remove("pubs/"+ name +".pub")


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

    def isCorerctJSON(string):
        try:
            json.loads(string)
        except Exception as e:
            print(str(e))
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
        json_correct = Validator.isCorerctJSON(string)
        if not json_correct:
            print(string)
            print("badly formatted json")
            self.reportBadSyntax("badly formatted json")
            return
        else:
            json_temp = json.loads(string)
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

    def reportBadSyntax(self, message=None):
        if message==None:
            message="bad request syntax"
        self.respond(300, "error", message)

    def hasSubID(self, IDL):
        for sub in self.subscriptions:
            if sub.IDL==IDL:
                return True
        return False

    def do(self, verb, attributes):
        if verb=="sub":
            self.__sub(attributes)
        elif verb=="new_pub":
            self.__new_pub(attributes) 
        elif verb=="delete_pub":
            self.__delete_pub(attributes)
        elif verb=="update_pub":
            self.__update_pub(attributes)
        else:
            print("bad verb")
            self.respond(300, "error", "unknown verb")

    def __sub(self, attributes):
        print("handling SUB request")
        if not Validator.attributesPresent(["id", "pub_name"], attributes):
            self.reportBadSyntax()
            return
        hasSub = self.hasSubID(attributes["id"])
        if hasSub:
            self.respond(422, "error", "you already have that id assigned to a publication. Unsub first or choose a different ID")
            return
        try:
            pub = publicationCollection.getPublicationByName(attributes["pub_name"])
        except PubNotFoundError:
            self.respond(404, "error", "publication not found")
            return
        sub = subscriptionCollection.new(self, pub, attributes["id"])
        self.subscriptions.append(sub)
        self.respondOK(pub.getContents())

    def __new_pub(self, attributes):
        if not Validator.attributesPresent(["name", "content"], attributes):
            self.reportBadSyntax("some attributes missing")
            return  
        if publicationCollection.nameTaken(attributes["name"]):
            self.respond(420, "error", "publication name already exists")
            return
        if not Validator.isCorerctJSON(attributes["content"]):
            self.reportBadSyntax("incorrect json in content")
            return
        publicationCollection.createPublication(attributes["name"], attributes["content"])
        self.respondOK("")

    def __delete_pub(self, attributes):
        if not Validator.attributesPresent(["name"], attributes):
            self.reportBadSyntax("'name' attribute missing")
            return  
        if not publicationCollection.nameTaken(attributes["name"]):
            self.respond(420, "error", "publication name does not exist")
            return
        publicationCollection.delete(attributes["name"])
        self.respondOK(200)

    def __update_pub(self, attributes):
        if not Validator.attributesPresent(["pub_name", "changes"], attributes):
            self.reportBadSyntax("some attributes missing")
            return          
        if not publicationCollection.nameTaken(attributes["pub_name"]):
            self.respond(404, "error", "publication name not found")
            return
        if not isinstance(attributes["changes"], list):
            self.reportBadSyntax("'changes' attribute must be a [] list")
            return
        patch = jsonpatch.JsonPatch(attributes["changes"])
        publication = publicationCollection.getPublicationByName(attributes['pub_name'])
        publication.applyPatch(patch)
        self.respondOK(publication.getContents())
        publication.propagate()

    def sendPubUpdate(self, publication):


    def respond(self, res_number, status, message):
            message = json.dumps({'res_number': res_number, 'status': status, 'message': message})
            print("sending", message)
            self.socket.send(bytes(message, "UTF-8"))

    def respondOK(self, message):
        self.respond(200, "ok", message)

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

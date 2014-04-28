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

from sys import path
path.append("classes/")

import subscription
import publication
import client


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

#wywoływana w osobny wątku, w nieblokujący sposób zczytuje informacje od połączonych klientów
def monitorClients():
    while 1:
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
                if error or len(data)==0:
                    client.Collection.connected_sockets.remove(socket)
                    print("client_temp", client_temp.IDL, "disconnected")
                    client_temp.unsubAll()
                    continue
                client_temp.parseIncomingJSON(data)
                #client.respond(200, "ok", "ok")

#kolekcja klientów

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
        elif verb=="replace_pub":
            self.__replace_pub(attributes)
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
        sub = subscription.Collection.new(self, pub, attributes["id"])
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
        publication.propagate("update")

    def __replace_pub(self, attributes):
        if not Validator.attributesPresent(["pub_name", "new_content"], attributes):
            self.reportBadSyntax("some attributes missing")
            return   
        if not publicationCollection.nameTaken(attributes["pub_name"]):
            self.respond(404, "error", "publication name not found")
            return
        publication = publicationCollection.getPublicationByName(attributes["pub_name"])
        publication.setContentByObject(attributes["new_content"])
        self.respondOK(publication.getContents())
        publication.propagate("replace")

    def respond(self, res_number, status, message):
            message = json.dumps({'res_number': res_number, 'status': status, 'message': message})
            print("sending", message)
            self.socket.send(bytes(message, "UTF-8"))

    def respondOK(self, message):
        self.respond(200, "ok", message)

    def unsubAll(self):
        for sub in self.subscriptions:
            self.subscriptions.remove(sub)
            subscription.Collection.remove(sub)

client_monitor_thread = threading.Thread (target=monitorClients, args=() )
client_monitor_thread.start()

publicationCollection = publication.PublicationCollection()

while 1:
    (new_clientSocket, address) =  serversocket.accept()
    client_new = Client(new_clientSocket, address)
    client.Collection.addClient(client_new)

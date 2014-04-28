import json
import validator
import publication
import subscription
try:
    import jsonpatch
except:
    print("jsonpatch package has to be installed for this script to run properly. Install it and run this script again")
    sys.exit()


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

class Client():
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.IDL = None
        self.subscriptions = []

    def handleIncomingJSON(self, string):
        #konwersja ciągu bajtów na stringa
        string = str(string, encoding='UTF-8')
        json_correct = validator.isCorerctJSON(string)
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
        if not validator.attributesPresent(["id", "pub_name"], attributes):
            self.reportBadSyntax()
            return
        hasSub = self.hasSubID(attributes["id"])
        if hasSub:
            self.respond(422, "error", "you already have that id assigned to a publication. Unsub first or choose a different ID")
            return
        try:
            pub = publication.Collection.getPublicationByName(attributes["pub_name"])
        except PubNotFoundError:
            self.respond(404, "error", "publication not found")
            return
        sub = subscription.Collection.new(self, pub, attributes["id"])
        self.subscriptions.append(sub)
        self.respondOK(pub.getContents())

    def __new_pub(self, attributes):
        if not validator.attributesPresent(["name", "content"], attributes):
            self.reportBadSyntax("some attributes missing")
            return  
        if publication.Collection.nameTaken(attributes["name"]):
            self.respond(420, "error", "publication name already exists")
            return
        if not validator.isCorerctJSON(attributes["content"]):
            self.reportBadSyntax("incorrect json in content")
            return
        publication.Collection.createPublication(attributes["name"], attributes["content"])
        self.respondOK("")

    def __delete_pub(self, attributes):
        if not validator.attributesPresent(["name"], attributes):
            self.reportBadSyntax("'name' attribute missing")
            return  
        if not publication.Collection.nameTaken(attributes["name"]):
            self.respond(420, "error", "publication name does not exist")
            return
        publication.Collection.delete(attributes["name"])
        self.respondOK(200)

    def __update_pub(self, attributes):
        if not validator.attributesPresent(["pub_name", "changes"], attributes):
            self.reportBadSyntax("some attributes missing")
            return          
        if not publication.Collection.nameTaken(attributes["pub_name"]):
            self.respond(404, "error", "publication name not found")
            return
        if not isinstance(attributes["changes"], list):
            self.reportBadSyntax("'changes' attribute must be a [] list")
            return
        patch = jsonpatch.JsonPatch(attributes["changes"])
        pub = publication.Collection.getPublicationByName(attributes['pub_name'])
        pub.applyPatch(patch)
        self.respondOK(pub.getContents())
        pub.propagate("update")

    def __replace_pub(self, attributes):
        if not validator.attributesPresent(["pub_name", "new_content"], attributes):
            self.reportBadSyntax("some attributes missing")
            return   
        if not publication.Collection.nameTaken(attributes["pub_name"]):
            self.respond(404, "error", "publication name not found")
            return
        pub = publication.Collection.getPublicationByName(attributes["pub_name"])
        pub.setContentByObject(attributes["new_content"])
        self.respondOK(pub.getContents())
        pub.propagate("replace")

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
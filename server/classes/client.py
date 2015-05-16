import json
import validator
import publication
import subscription
try:
    import jsonpatch
except:
    print("jsonpatch package has to be installed for this script to run properly. Install it and run this script again")
    sys.exit()


class PubNotFoundError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):  
        return repr(self.value)

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
            if "request_id" in json_temp:
                request_id=json_temp["request_id"]
            else:
                request_id=None
            self.do(verb, attributes, request_id)
        else:
            self.reportBadSyntax()

    def reportBadSyntax(self, message=None, request_id=None):
        if message==None or message=="":
            message="bad request syntax"
        self.respond(300, "error", message, request_id)

    def hasSubID(self, IDL):
        for sub in self.subscriptions:
            if sub.IDL==IDL:
                return True
        return False

    def do(self, verb, attributes, request_id):
        if verb=="sub":
            self.__sub(attributes, request_id)
        elif verb=="new_pub":
            self.__new_pub(attributes, request_id) 
        elif verb=="delete_pub":
            self.__delete_pub(attributes, request_id)
        elif verb=="update_pub":
            self.__update_pub(attributes, request_id)
        elif verb=="replace_pub":
            self.__replace_pub(attributes, request_id)
        else:
            print("bad verb")
            self.respond(300, "error", "unknown verb")

    def __sub(self, attributes, request_id):
        print("handling SUB request")
        if not validator.attributesPresent(["id", "pub_name"], attributes):
            self.reportBadSyntax("", request_id)
            return
        hasSub = self.hasSubID(attributes["id"])
        if hasSub:
            self.respond(422, "error", "you already have that id assigned to a publication. Unsub first or choose a different ID", request_id)
            return
        try:
            pub = publication.Collection.getPublicationByName(attributes["pub_name"])
        except publication.PubNotFoundError:
            self.respond(404, "error", "publication not found", request_id)
            return
        sub = subscription.Collection.new(self, pub, attributes["id"])
        self.subscriptions.append(sub)
        self.respondOK(pub.getContentsAsObject(), request_id)

    def __new_pub(self, attributes, request_id):
        if not validator.attributesPresent(["name", "content"], attributes):
            self.reportBadSyntax("some attributes missing", request_id)
            return  
        if publication.Collection.nameTaken(attributes["name"]):
            self.respond(420, "error", "publication name already exists", request_id)
            return
        #if not validator.isCorerctJSON(attributes["content"]):
        #    self.reportBadSyntax("incorrect json in content", request_id)
        #    return
        publication.Collection.createPublication(attributes["name"], attributes["content"])
        self.respondOK(None,  request_id)

    def __delete_pub(self, attributes, request_id):
        if not validator.attributesPresent(["name"], attributes):
            self.reportBadSyntax("'name' attribute missing", request_id)
            return  
        if not publication.Collection.nameTaken(attributes["name"]):
            self.respond(420, "error", "publication name does not exist", request_id)
            return
        publication.Collection.delete(attributes["name"])
        self.respondOK("ok", request_id)

    def __update_pub(self, attributes, request_id):
        if not validator.attributesPresent(["pub_name", "changes"], attributes):
            self.reportBadSyntax("some attributes missing",request_id)
            return          
        if not publication.Collection.nameTaken(attributes["pub_name"]):
            self.respond(404, "error", "publication name not found", request_id)
            return
        if not isinstance(attributes["changes"], list):
            self.reportBadSyntax("changes attribute must be a [] list",request_id)
            return
        patch = jsonpatch.JsonPatch(attributes["changes"])
        pub = publication.Collection.getPublicationByName(attributes['pub_name'])
        try:
            pub.applyPatch(patch)
        except:
            self.reportBadSyntax("badly formatted JsonPatch")
        self.respondOK(pub.getContentsAsObject(), request_id)
        pub.propagate("update")

    def __replace_pub(self, attributes, request_id):
        if not validator.attributesPresent(["pub_name", "new_content"], attributes):
            self.reportBadSyntax("some attributes missing",request_id)
            return   
        if not publication.Collection.nameTaken(attributes["pub_name"]):
            self.respond(404, "error", "publication name not found",request_id)
            return
        pub = publication.Collection.getPublicationByName(attributes["pub_name"])
        pub.setContentByObject(attributes["new_content"])
        self.respondOK(pub.getContentsAsObject(),request_id)
        pub.propagate("replace")

    def respond(self, res_number, status, message, request_id):
            message = json.dumps({'res_number': res_number, 'status': status, 'message': message, "request_id":request_id })
            print("sending", message)
            self.socket.send(bytes(message, "UTF-8"))

    def respondOK(self, message, request_id):
        self.respond(200, "ok", message, request_id)

    def unsubAll(self):
        for sub in self.subscriptions:
            self.subscriptions.remove(sub)
            subscription.Collection.remove(sub)
import json

class Subscription():
    def __init__(self, client, publication, IDL):
        self.client = client
        self.publication = publication
        self.IDL=IDL

    def sendUpdate(self, changes, typeL="update"):
        response = {"verb":"sub_push", "attributes":{"sub_id": self.IDL, "change_type": typeL, "content":changes}}
        print(response)
        message = json.dumps(response)
        print("responding:", response)
        self.client.socket.send(bytes(message, "UTF-8"))


class Collection:
    subscriptions = []
    subscriptionsByPub = {}

    @staticmethod
    def indexSubByPub(sub):
        if not sub.publication.name in Collection.subscriptionsByPub:
            Collection.subscriptionsByPub[sub.publication.name]=[]
        Collection.subscriptionsByPub[sub.publication.name].append(sub)

    @staticmethod
    def getSubsByPubName(pub_name):
        return subscriptionsByPub[pub_name]

    @staticmethod
    def new(client, publication, idL):
        sub = Subscription(client, publication, idL)
        Collection.subscriptions.append(sub)
        Collection.indexSubByPub(sub)
        return sub

    def remove( sub):
        Collection.subscriptions.remove(sub)
import os
import json
import jsonpatch
import subscription

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
            print(e)
            raise BadJSONSyntaxError(e.value)
        self.last_propagated_content = self.parsed_content
        self.name="publication_name_placeholder"
        self.file.close()

    def getContents(self):
        return self.content

    def getContentsAsObject(self):
        return json.loads(self.content)

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
        f.close()

    def propagate(self, typeL="update"):
        print("in propagate")
        changes = json.loads(jsonpatch.make_patch(self.last_propagated_content, self.getContentsAsObject()).to_string())
        subs = self.getSubscriptions()
        print(subs)
        for sub in subs:
            sub.sendUpdate(changes, typeL)
        self.last_propagated_content = self.content

    def getSubscriptions(self):
        list = []
        print("all subs:", subscription.Collection.subscriptions)
        for sub in subscription.Collection.subscriptions:
            if sub.publication.IDL==self.IDL:
                list.append(sub)
        return list

class Collection:

    def getPublicationByName(name):
        try:
            pub= Publication(name)
        except BadJSONSyntaxError:
            print('publication content invalid')
            raise PubDamagedError("Publication content is not valid")
        except:
            raise PubNotFoundError("Publication not found")
        return pub

    def nameTaken(name):
        try:
            f=open("pubs/"+name+".pub")
        except FileNotFoundError:
            return False
        f.close()
        return True

    def createPublication(name, content_obj):
        f = open("pubs/" + name + ".pub", "a")
        f.write(json.dumps(content_obj))
        f.close()
        return Publication(name)

    def delete(name):
        os.remove("pubs/"+ name +".pub")
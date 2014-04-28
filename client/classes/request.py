import uuid
import json
import copy

class Request():
	def __init__(self, body):
		self.body = body #object, not stirng
		self.waiting = True
		self.id = uuid.uuid4()
		self.response_obj = None

	def setServerResponse(self, response_obj):
		self.waiting = False
		self.response_obj = response_obj

	def getBodyString(self):
		temp_obj = copy.deepcopy(self.body)
		temp_obj["request_id"] = str(self.id)
		print("about to send", temp_obj)
		return json.dumps(temp_obj)

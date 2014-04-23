import json

try:
	res = json.loads('lolo')
except ValueError:
	print("badly formatted json!")
print(res["a"])
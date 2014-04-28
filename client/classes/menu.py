import subscription
import publication

def display():
	print("Hi, user! Choose one option from the list below:")
	print("1 - subcribe a publication")
	print("2 - unsubcribe from a publication")
	print("3 - create a publication")
	print("4 - to update a publication")
	print("5 - to replace a publication")
	print("6 - to delete a publication")
	print("7 - to view live publication content")
	print("0 - to exit")

	menu = input("What do you want to do:")
	if menu == "1":
		#sub
		pub_name = input("publication name:")
		try:
			subscription.newSub(pub_name)
		except:
			return
			print("Publication does not exist.")
		return
	elif menu == "2":
		#unsub
		pub_id = getSubIndex("From which one?")
		if not pub_id==None:
			pub_id=int(pub_id)
			subscription.unsub(pub_id)
	elif menu == "3":
		#new_pub
		title=input("New publication's name:")
		content=input("\"" + title + "\"'s content:")
		res = publication.create(title, content)
		if res==-1:
			print("\n\n\ninvalid json content\n\n")
		elif res==-2:
			print("\n\n\nname already taken\n\n")
		else:
			print("\n\n\npublication created succesfully\n\n")
	elif menu == "4":
		#update_pub
		pub_name = input("Name of the pub you want to update:")
		patch = input("Please provide proper JSONPatch you want to apply to '" + pub_name +"':")
		res = publication.update(pub_name, patch)
		if res==-1:
			print("\n\n\ninvalid patch\n\n\n")
		elif res==-2:
			print("\n\n\nPublication " + pub_name + " does not exist\n\n\n")
		elif res==-3:
			print("\n\n\npatch must be a correct json string\n\n\n")
		elif res==0:
			print("\n\n\nchanges applied!\n\n\n")
		else:
			print("unknown error")
	elif menu == "5":
		#replace_pub
		pub_name = input("Publication name:")
		new_content = input("New json with content of " + pub_name + ":")
		res = publication.replace(pub_name, new_content)
		if res==-3:
			print("\n\n\nincorrect json string")
		elif res==-1:
			print("\n\n\npublication", pub_name, "does not exist\n\n\n")
		elif res==-100:
			print("\n\n\nunknown error occured\n\n\n")
		else:
			print("\n\n\npublication replaced succesfully!\n\n\n")
	elif menu == "6":
		#delete_pub
		pub_name = input("Name of publication to delete:")
		res = publication.delete(pub_name)
		if res==0:
			print("\n\n\nPublication deleted succesfully\n\n\n")
		elif res==-1:
			print("\n\n\nPublication", pub_name, "does not exist\n\n\n")
		else:
			print("unknown error")
	elif menu =="7":
		#live pub preview:
		sub_index = getSubIndex()
		if not sub_index==None:
			sub_index=int(sub_index)
			subscription.collection[sub_index].display()
			input()
		return
	elif menu == "0":
		exit = 1
	else:
		print("Sorry, I don't know what do you want to do.")
		return
	return

def enlistSubscriptions():
	if len(subscription.collection)==0:
		print("\n\n\nCurrently not subscribed to any publication. Subscribe to something first\n\n")
		print()
		return False
	else:
		i=0;
		for sub in subscription.collection:
			print(i, " - subscription on ", sub.pub_name)
			i+=1
		return True

def getSubIndex(message="Choose subscription"):
	print(message)
	if enlistSubscriptions():
		return input("Your choice:")
	else:
		return None
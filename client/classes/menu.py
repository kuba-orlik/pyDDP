import subscription

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
		pub_name = input("publication name:")
		try:
			subscription.newSub(pub_name)
		except:
			return
			print("Publication does not exist.")
		return
	elif menu == "2":
		pub_id = getSubIndex("From which one?")
		if not pub_id==None:
			pub_id=int(pub_id)
			subscription.unsub(pub_id)
	elif menu == "3":
		json = input("json:")
		add_pub(json)
	elif menu == "4":
		pub_id = input("publication id:")
		json = input("json:")
		update_pub(pub_id, json)
	elif menu == "5":
		pub_id = input("publication id:")
		json = input("json:")
		replace_pub(pub_id, json)
	elif menu == "6":
		pub_id = input("publication id:")
		delete_pub(pub_id)
	elif menu == "0":
		exit = 1
	else:
		print("Sorry, I don't know what do you want to do.")
		return
	return

def enlistSubscriptions():
	if len(subscription.collection)==0:
		print("Currently not subscribed to any publication")
		print()
		return False
	else:
		i=0;
		for sub in subscription.collection:
			print(i, " - subscription on ", sub.pub_name)
			i+=1
		return True

def getSubIndex(message):
	print(message)
	if enlistSubscriptions():
		return input("Your choice:")
	else:
		return None
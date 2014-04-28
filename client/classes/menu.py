def display():
	print("Hi, user! Choose one option from the list below:")
	print("1 - to subcribe a publication")
	print("2 - to unsubcribe a publication")
	print("3 - to add a publication")
	print("4 - to update a publication")
	print("5 - to replace a publication")
	print("6 - to delete a publication")
	print("0 - to exit")

	menu = input("What do you want to do:")
	print(menu)
	if menu == "1":
		pub_id = input("publication id:")
		sub(pub_id)
	elif menu == "2":
		pub_id = input("publication id:")
		unsub(pub_id)
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
		print("Sorry, I don't know what do you watn to do.")
exit = 0;
while exit == 0:
    print("Hi, user! Choose one option from the list below:");
    print("1 - to subcribe a publication");
    print("2 - to unsubcribe a publication");
    print("3 - to add a publication");
    print("4 - to update a publication");
    print("5 - to raplace a publication");
    print("6 - to delete a publication");
    print("0 - to exit")

    menu = input("What do you want to do:")
    print(menu)
    if menu == "1":
        pub_id = input("publication id:")

    elif menu == "2":
        pub_id = input("publication id:")
    elif menu == "3":
        pub_id = input("publication id:")
    elif menu == "4":
        pub_id = input("publication id:")
    elif menu == "5":
        pub_id = input("publication id:")
    elif menu == "6":
        pub_id = input("publication id:")
    elif menu == "0":
        exit = 1;
    else:
        print("Sorry, I don't know what do you watn to do.")

def menu(choices):
    for idx, item in enumerate(choices):
        print("{0} - {1}".format(idx+1, item))

    choice = int(input("choose an option: "))

    return choice
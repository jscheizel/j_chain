jenichain = [[1]]
input_text = "Please type your transaction amount: "
quit_jenichain = False
start = True

def get_last_jenichain_entry():
    return jenichain[-1]


def add_value(jeni):
    jenichain.append([get_last_jenichain_entry(), jeni])


def get_transaction_input():
    return float(input(input_text))


def get_user_decision():
    return input("What do you want to do?: ")


def print_possibilities():
    print("Type 'T' for adding a transaction or 'Q' for quitting the program.")


def print_jenichain_elements():
    for jeni in jenichain:
        print("Jeni: ")
        print(jeni)


def validate_jenichain():
    index = 0
    for jeni in jenichain:
	
        if index > 0 and jeni != jenichain[index-1]:
            print("Die chain wurde geändert")
            break
        index += 1


while not quit_jenichain:
    if start:
        print_possibilities()
        start = False

    decision = get_user_decision()
    if decision == "Q":
        quit_jenichain = True
        print_jenichain_elements()
    elif decision == "T":
        amount = get_transaction_input()
        add_value(amount)
    else:
        print("This action is not available!")

    if not validate_jenichain():
        break


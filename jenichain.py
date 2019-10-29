import functools
import hashlib
import hash_util
from collections import OrderedDict


def get_last_entry(jenichain):
    return jenichain[-1]


def verify_transaction(jenichain, transaction, open_transactions):
    return get_balance(jenichain, transaction["sender"], open_transactions) >= transaction["amount"]


def add_transaction(jenichain, open_transactions, sender, recipient, amount):
    transaction = OrderedDict([("sender", sender), ("recipient",recipient), ("amount", amount)])
    if verify_transaction(jenichain, transaction, open_transactions):
        open_transactions.append(transaction)
    else:
        print("This Transaction is not possible, as it exceeds your balance!")


def check_valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hashlib.sha3_256(guess).hexdigest()
    return guess_hash[0:2] == '00'


def proof_of_work(open_transactions, hash_value):
    nounce = 0
    while not check_valid_proof(open_transactions, hash_value, nounce):
        nounce += 1
    return nounce


def mine_block(jenichain, open_transactions, miner):
    last_block = get_last_entry(jenichain)

    hash_value = hash_util.hash_block(last_block)
    pow = proof_of_work(open_transactions, hash_value)

    mining_transaction = OrderedDict([("sender", "MINING"), ("recipient", miner), ("amount", 1)])
    open_transactions.append(mining_transaction)

    block = {
        "previous_hash": hash_value,
        "index": len(jenichain),
        "transactions": open_transactions,
        "proof": pow
    }
    jenichain.append(block)


def sum_numbers_in_list(number_list):
    list_sum = 0
    for element in number_list:
        if len(element) > 0:
            list_sum += int(element[0])
    return list_sum


def get_balance(jenichain, participant, open_transactions):
    amounts_send = [[transaction['amount'] for transaction in block['transactions'] if transaction["sender"] == participant] for block in jenichain]
    amounts_send_in_progress = [transaction['amount'] for transaction in open_transactions if transaction["sender"] == participant]
    amounts_send.append(amounts_send_in_progress)
    amounts_recieved = [[transaction['amount'] for transaction in block['transactions'] if transaction["recipient"] == participant] for block in jenichain]

    amount_recieved = functools.reduce(lambda summe, amounts: summe + sum(amounts) if len(amounts) > 0 else summe + 0, amounts_recieved, 0)  # function, list, start index
    amount_send = functools.reduce(lambda summe, amounts: summe + sum(amounts) if len(amounts) > 0 else summe + 0, amounts_send, 0)  # function, list, start index

    return amount_recieved - amount_send


def get_transaction_input():
    input_amount = "Please type your transaction amount: "
    input_recipient = "Please type your transaction recipient: "
    recipient = input(input_recipient)
    amount = float(input(input_amount))
    return recipient, amount


def get_user_decision():
    return input("What do you want to do?: ")


def print_possibilities():
    print("Type 'T' for adding a transaction or 'Q' for quitting the program.")


def print_jenichain_elements(jenichain):
    for jeni in jenichain:
        print("Jeni: ")
        print(jeni)


def validate_jenichain(jenichain):
    for (jeni_index, block) in enumerate(jenichain):
        if jeni_index > 0:
            if block['previous_hash'] != hash_util.hash_block(jenichain[jeni_index-1]):
                print("Die chain wurde geändert")
                return False
            if not check_valid_proof(block["transactions"][:-1], block["previous_hash"], block["proof"]):
                print("Proof of work is not valid")
                return False
    return True


def mine_initial_entry():
    return {
        "previous_hash": "",
        "index": 0,
        "transactions": [],
        "proof": 100
    }


def run_jenichain():
    participants = {"Jeni", "Thorsten"}
    jenichain = [mine_initial_entry()]
    open_transactions = []
    quit_jenichain = False
    start = True
    owner = "Jeni"

    while not quit_jenichain:
        if start:
            print_possibilities()
            start = False

        decision = get_user_decision()
        if decision == "Q":  # quit
            quit_jenichain = True
            print_jenichain_elements(jenichain)
        elif decision == "T":  # transaction
            recipient, amount = get_transaction_input()
            sender = owner  # for testing
            add_transaction(jenichain, open_transactions, sender, recipient, amount)
        elif decision == "M":  # mine block
            miner = owner  # for testing
            mine_block(jenichain, open_transactions, miner)
            open_transactions = []
        elif decision == "P":  # Particioants
            print([participant + ": " + str(get_balance(jenichain, participant, open_transactions)) for participant in participants])
        elif decision == "C":  # Change blocks
            if jenichain.__len__() > 1:
                jenichain[0] = {
                    "previous_hash": "",
                    "index": 1,  # value changed from 0 to 1
                    "transactions": []
                }
        else:
            print("This action is not available!")

        if not validate_jenichain(jenichain):
            break


run_jenichain()

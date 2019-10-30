from jenichain import JeniChain
from uuid import uuid4
from verification import Verification


class Node:

    def __init__(self):
        self.node_id = str(uuid4())
        self.jenichain = JeniChain(self.node_id)
        self.participants = {self.node_id, "Thorsten"}

    def listen_for_input(self):
        quit_jenichain = False
        start = True

        while not quit_jenichain:
            if start:
                self.print_possibilities()
                start = False

            decision = self.get_user_decision()
            if decision == "Q":  # quit
                quit_jenichain = True
                self.print_jenichain_elements()
            elif decision == "T":  # transaction
                recipient, amount = self.get_transaction_input()
                self.jenichain.add_transaction(self.node_id, recipient, amount)
            elif decision == "M":  # mine block
                self.jenichain.mine_block()
            elif decision == "P":  # Participants
                print([participant + ": " + str(self.jenichain.get_balance()) for
                       participant in self.participants])
            else:
                print("This action is not available!")

            if not Verification.validate_jenichain(self.jenichain):
                break

    def get_user_decision(self):
        return input("What do you want to do?: ")

    def print_possibilities(self):
        print("Type 'T' for adding a transaction or 'Q' for quitting the program.")

    def print_jenichain_elements(self):
        for jeni in self.jenichain:
            print("Jeni: ")
            print(jeni)

    def get_transaction_input(self):
        input_amount = "Please type your transaction amount: "
        input_recipient = "Please type your transaction recipient: "
        recipient = input(input_recipient)
        amount = float(input(input_amount))
        return recipient, amount


node = Node()
node.listen_for_input()

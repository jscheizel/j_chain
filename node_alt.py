from j_chain import J_Chain
from uuid import uuid4
from util.verification import Verification
from wallet import Wallet


class Node:

    def __init__(self):
        # self.node_id = str(uuid4())
        self.wallet = Wallet()
        self.j_chain = J_Chain(self.wallet.public_key)
        self.participants = ["Thorsten"]

    def listen_for_input(self):

        start = True

        quit_j_chain = self.load_or_create_wallet()

        while not quit_j_chain:
            if start:
                self.print_possibilities()
                start = False

            decision = self.get_user_decision()
            if decision == "Q":  # quit
                quit_j_chain = True
                self.print_j_chain_elements()
            elif decision == "T":  # transaction
                if self.wallet.public_key is None:
                    print("You got no wallet, please load (L) or create (W) one.")
                else:
                    recipient, amount = self.get_transaction_input()
                    signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                    self.j_chain.add_transaction(self.wallet.public_key, recipient, signature, amount)
            elif decision == "M":  # mine block
                if self.wallet.public_key is None:
                    print("You got no wallet, please load (L) or create (W) one.")
                else:
                    self.j_chain.mine_block()
            elif decision == "P":  # Participants
                print([participant + ": " + str(self.j_chain.get_balance(participant)) for
                       participant in self.participants])
            else:
                print("This action is not available!")

            if not Verification.validate_j_chain(self.j_chain.chain):
                break

    def load_or_create_wallet(self):
        no_wallet = True
        while no_wallet:
            self.print_wallet_possibilities()
            decision = self.get_user_decision()
            if decision == "W":  # Create Wallet
                self.wallet.create_keys()
                self.j_chain = J_Chain(self.wallet.public_key)
                self.participants.append(self.wallet.public_key)
                self.wallet.save_keys()
                return False  # not quit_chain
            elif decision == "L":
                self.wallet.load_key()
                self.j_chain = J_Chain(self.wallet.public_key)
                self.participants.append(self.wallet.public_key)
                return False  # not quit_chain
            elif decision == "Q":
                return True  # Quit chain
            else:
                print("This action is not available!")

    @staticmethod
    def print_wallet_possibilities():
        print("Type 'W' for creating a wallet or 'L' for loading a wallet or 'Q' for quitting the program.")


    @staticmethod
    def get_user_decision():
        return input("What do you want to do?: ")

    @staticmethod
    def print_possibilities():
        print("Type 'T' for transaction, 'M' for mining, or 'Q' for quitting the program.")

    def print_j_chain_elements(self):
        for block in self.j_chain.chain:
            print("Block: ")
            print(block)

    @staticmethod
    def get_transaction_input():
        input_amount = "Please type your transaction amount: "
        input_recipient = "Please type your transaction recipient: "
        recipient = input(input_recipient)
        amount = float(input(input_amount))
        return recipient, amount


if __name__ == "__main__":
    node = Node()
    node.listen_for_input()

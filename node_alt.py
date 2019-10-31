from jenichain import JeniChain
from uuid import uuid4
from util.verification import Verification
from wallet import Wallet


class Node:

    def __init__(self):
        # self.node_id = str(uuid4())
        self.wallet = Wallet()
        self.jenichain = JeniChain(self.wallet.public_key)
        self.participants = ["Thorsten"]

    def listen_for_input(self):

        start = True

        quit_jenichain = self.load_or_create_wallet()

        while not quit_jenichain:
            if start:
                self.print_possibilities()
                start = False

            decision = self.get_user_decision()
            if decision == "Q":  # quit
                quit_jenichain = True
                self.print_jenichain_elements()
            elif decision == "T":  # transaction
                if self.wallet.public_key is None:
                    print("You got no wallet, please load (L) or create (W) one.")
                else:
                    recipient, amount = self.get_transaction_input()
                    signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                    self.jenichain.add_transaction(self.wallet.public_key, recipient, signature, amount)
            elif decision == "M":  # mine block
                if self.wallet.public_key is None:
                    print("You got no wallet, please load (L) or create (W) one.")
                else:
                    self.jenichain.mine_block()
            elif decision == "P":  # Participants
                print([participant + ": " + str(self.jenichain.get_balance(participant)) for
                       participant in self.participants])
            else:
                print("This action is not available!")

            if not Verification.validate_jenichain(self.jenichain):
                break

    def load_or_create_wallet(self):
        no_wallet = True
        while no_wallet:
            self.print_wallet_possibilities()
            decision = self.get_user_decision()
            if decision == "W":  # Create Wallet
                self.wallet.create_keys()
                self.jenichain = JeniChain(self.wallet.public_key)
                self.participants.append(self.wallet.public_key)
                self.wallet.save_keys()
                return False  # not quit_jenichain
            elif decision == "L":
                self.wallet.load_key()
                self.jenichain = JeniChain(self.wallet.public_key)
                self.participants.append(self.wallet.public_key)
                return False  # not quit_jenichain
            elif decision == "Q":
                return True  # Quit Jenichain
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

    def print_jenichain_elements(self):
        for jeni in self.jenichain.chain:
            print("Jeni: ")
            print(jeni)

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

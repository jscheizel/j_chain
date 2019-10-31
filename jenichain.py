import functools
from util import hash_util
from util.file_util import FileHandler
from transactions import Transaction
from jeniblock import JeniBlock
from util.verification import Verification
from wallet import Wallet


class JeniChain:

    MINING_REWARD = 1

    def __init__(self, node):
        self.chain = [self.get_initial_entry()]
        self.open_transactions = []
        self.chain, self.open_transactions = FileHandler.load_data(self.chain, self.open_transactions)
        self.node = node

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, chain):
        self.__chain = chain

    def get_last_entry(self):
        return self.chain[-1]

    def add_transaction(self, sender, recipient, signature, amount):
        transaction = Transaction(sender, recipient, signature, amount)
        if Wallet.verify_signture(transaction):
            if Verification.verify_transaction(transaction, sender, self.get_balance):
                self.open_transactions.append(transaction)
                FileHandler.save_jenichain(self)
            else:
                print("This Transaction is not possible, as it exceeds your balance!")
        else:
            print("The Signature of this transaction is not valid")

    def proof_of_work(self, hash_value):
        nounce = 0
        while not Verification.check_valid_proof(self.open_transactions, hash_value, nounce):
            nounce += 1
        return nounce

    def mine_block(self):
        last_block = self.get_last_entry()

        hash_value = hash_util.hash_block(last_block)
        proof = self.proof_of_work(hash_value)

        mining_transaction = Transaction("MINING", self.node, "", self.MINING_REWARD)
        self.open_transactions.append(mining_transaction)

        block = JeniBlock(len(self.chain), hash_value, self.open_transactions, proof)
        if self.transaction_signature_is_valid(block):
            self.__chain.append(block)
            self.open_transactions = []
            FileHandler.save_jenichain(self)
        else:
            print("Fehler: Die Transactionen wurden geändert")

    @staticmethod
    def transaction_signature_is_valid(block):
        for transaction in block.transactions:
            if not Wallet.verify_signture(transaction):
                return False
        return True

    def get_balance(self, participant):
        amounts_send = [[transaction.amount for transaction in block.transactions
                         if transaction.sender == participant] for block in self.chain]
        amounts_send_in_progress = [transaction.amount for transaction in self.open_transactions
                                    if transaction.sender == participant]
        amounts_send.append(amounts_send_in_progress)
        amounts_recieved = [[transaction.amount for transaction in block.transactions
                             if transaction.recipient == participant] for block in self.chain]

        # function, list, start index
        amount_recieved = functools.reduce(lambda summe, amounts: summe + sum(amounts)
                                                if len(amounts) > 0 else summe + 0, amounts_recieved, 0)
        amount_send = functools.reduce(lambda summe, amounts: summe + sum(amounts)
                                                if len(amounts) > 0 else summe + 0, amounts_send, 0)

        return amount_recieved - amount_send

    @staticmethod
    def get_initial_entry():
        return JeniBlock(0, "", [], 100, 0)

    @staticmethod
    def sum_numbers_in_list(number_list):
        list_sum = 0
        for element in number_list:
            if len(element) > 0:
                list_sum += int(element[0])
        return list_sum

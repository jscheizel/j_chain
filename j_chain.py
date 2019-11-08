import functools
from util import hash_util
from util.file_util import FileHandler
from transactions import Transaction
from jblock import JBlock
from util.verification import Verification
from wallet import Wallet
import requests


class J_Chain:

    MINING_REWARD = 1

    def __init__(self, node, port):
        self.chain = [self.get_initial_entry()]
        self.open_transactions = []
        self.__peer_nodes = set()
        self.chain, self.open_transactions, self.__peer_nodes = FileHandler.load_data(self.chain, self.open_transactions, self.__peer_nodes, port)
        self.node = node
        self.port = port
        self.resolve_conflicts = False

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, chain):
        self.__chain = chain

    def get_last_entry(self):
        return self.chain[-1]

    def add_transaction(self, sender, recipient, signature, amount, broadcast=False):
        # if self.node is None:
        #     return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Wallet.verify_signture(transaction):
            if Verification.verify_transaction(transaction, sender, self.get_balance):
                self.open_transactions.append(transaction)
                FileHandler.save_j_chain(self)
                if not broadcast:
                    for node in self.__peer_nodes:
                        url = "http://{}/broadcast-transaction".format(node)
                        try:
                            response = requests.post(url, json={"sender":sender, "recipient":recipient, "amount":amount, "signature":signature})
                            if response.status_code == 400 or response.status_code == 500:
                                print("Transaction declined, needs resolving")
                                return False
                        except requests.exceptions.ConnectionError:
                            continue
                    return True
            else:
                print("This Transaction is not possible, as it exceeds your balance!")
                return False
        else:
            print("The Signature of this transaction is not valid")
            return False
        return True

    def proof_of_work(self, hash_value):
        nounce = 0
        while not Verification.check_valid_proof(self.open_transactions, hash_value, nounce):
            nounce += 1
        return nounce

    def mine_block(self):
        if self.node is None:
            return None

        last_block = self.get_last_entry()

        hash_value = hash_util.hash_block(last_block)
        proof = self.proof_of_work(hash_value)

        mining_transaction = Transaction("MINING", self.node, "", self.MINING_REWARD)
        self.open_transactions.append(mining_transaction)

        block = JBlock(len(self.chain), hash_value, self.open_transactions, proof)
        if self.transaction_signature_is_valid(block):
            self.__chain.append(block)
            self.open_transactions = []
            FileHandler.save_j_chain(self)
            for node in self.__peer_nodes:
                url = "http://{}/broadcast-block".format(node)
                try:
                    converted_block = block.__dict__.copy()
                    converted_block["transactions"] = [transaction.__dict__ for transaction in converted_block["transactions"]]
                    response = requests.post(url, json={"block": converted_block})
                    if response.status_code == 400 or response.status_code == 500:
                        print("block declined, needs resolving")
                    if response.status_code == 409:
                        self.resolve_conflicts = True
                except requests.exceptions.ConnectionError:
                    continue
            return block
        else:
            print("Fehler: Die Transactionen wurden geändert")
            return None

    @staticmethod
    def transaction_signature_is_valid(block):
        for transaction in block.transactions:
            if not Wallet.verify_signture(transaction):
                return False
        return True

    def get_balance(self, participant):
        if participant is None:
            return None

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

    def add_block(self, block):
        transactions = [Transaction(transaction["sender"], transaction["recipient"], transaction["signature"], transaction["amount"]) for transaction in block["transactions"]]
        proof_is_valid = Verification.check_valid_proof(transactions[:-1], block["previous_hash"], block["proof"])
        hashes_match = hash_util.hash_block(self.chain[-1]) == block["previous_hash"]
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = JBlock(block["index"], block["previous_hash"], transactions, block["proof"], block["timestamp"])
        self.__chain.append(converted_block)
        stored_transactions = self.open_transactions[:]
        for incoming in block["transactions"]:
            for open_transaction in stored_transactions:
                sender_and_recipient_equal = open_transaction.sender == incoming["sender"] and open_transaction.recipient == incoming["recipient"]
                signature_equal = open_transaction.signature == incoming["signature"]
                amount_equal = open_transaction.amount == incoming["amount"]
                if sender_and_recipient_equal and signature_equal and amount_equal:
                    try:
                        self.open_transactions.remove(open_transaction)
                    except ValueError:
                        print("item already removed")
        FileHandler.save_j_chain(self)
        return True

    def resolve(self):
        winner_chain = self.chain
        replace = False
        for node in self.__peer_nodes:
            url = "http://{}/chain".format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [JBlock(block["index"], block["previous_hash"],
                                     [Transaction(transaction["sender"], transaction["recipient"], transaction["signature"], transaction["amount"]) for transaction in block["transactions"]],
                                     block["proof"], block["timestamp"]) for block in node_chain]

                node_chain_lenght = len(node_chain)
                local_chain_lenght = len(self.chain)
                if node_chain_lenght > local_chain_lenght and Verification.validate_j_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        self.chain = winner_chain
        if replace:
            self.open_transactions = []
        FileHandler.save_j_chain(self)
        return replace

    @staticmethod
    def get_initial_entry():
        return JBlock(0, "", [], 100, 0)

    @staticmethod
    def sum_numbers_in_list(number_list):
        list_sum = 0
        for element in number_list:
            if len(element) > 0:
                list_sum += int(element[0])
        return list_sum

    def add_peer_node(self, node):
        self.__peer_nodes.add(node)
        FileHandler.save_j_chain(self)

    def remove_peer_node(self, node):
        self.__peer_nodes.discard(node)
        FileHandler.save_j_chain(self)

    def get_peer_nodes(self):
        return list(self.__peer_nodes)

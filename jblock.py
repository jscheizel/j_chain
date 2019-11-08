from time import time
from util.printable import Printable


class JBlock(Printable):

    def __init__(self, index, previous_hash, transactions, proof, timestamp=None):
        self.proof = proof
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions  # transactions object
        self.timestamp = self.timestamp = time() if timestamp is None else timestamp

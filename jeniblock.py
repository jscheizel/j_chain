from time import time
from printable import Printable


class JeniBlock(Printable):

    def __init__(self, index, previous_hash, transactions, proof, timestamp=None):
        self.proof = proof
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions  # transactions object
        self.timestamp = self.timestamp = time() if timestamp is None else timestamp

import hashlib
import json


def hash_block(block):
    hashable_block = block.__dict__.copy()
    hashable_block["transactions"] = [transaction.to_odered_dict() for transaction in hashable_block["transactions"]]
    return hashlib.sha256(json.dumps(hashable_block, sort_keys=True).encode()).hexdigest()

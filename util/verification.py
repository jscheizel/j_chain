from util import hash_util
import hashlib


class Verification:

    @classmethod
    def validate_jenichain(cls, jenichain):
        for (jeni_index, block) in enumerate(jenichain.chain):
            if jeni_index > 0:
                if block.previous_hash != hash_util.hash_block(jenichain.chain[jeni_index - 1]):
                    print("Die chain wurde geändert")
                    return False
                if not cls.check_valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                    print("Proof of work is not valid")
                    return False
        return True

    @staticmethod
    def verify_transaction(transaction, sender, get_balance):
        return get_balance(sender) >= transaction.amount

    @staticmethod
    def check_valid_proof(transactions, last_hash, proof):
        guess = (str([transaction.to_odered_dict() for transaction in transactions]) + str(last_hash) + str(
            proof)).encode()
        guess_hash = hashlib.sha3_256(guess).hexdigest()
        return guess_hash[0:2] == '00'

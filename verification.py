import hash_util
import hashlib


class Verification:

    def validate_jenichain(self, jenichain):
        for (jeni_index, block) in enumerate(jenichain.chain):
            if jeni_index > 0:
                if block.previous_hash != hash_util.hash_block(jenichain.chain[jeni_index-1]):
                    print("Die chain wurde geändert")
                    return False
                if not self.check_valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                    print("Proof of work is not valid")
                    return False
        return True

    def verify_transaction(self, jenichain, transaction, open_transactions, get_balance):
        return get_balance(jenichain, transaction.sender, open_transactions) >= transaction.amount

    def check_valid_proof(self, transactions, last_hash, proof):
        guess = (str([transaction.to_odered_dict() for transaction in transactions]) + str(last_hash) + str(
            proof)).encode()
        guess_hash = hashlib.sha3_256(guess).hexdigest()
        return guess_hash[0:2] == '00'

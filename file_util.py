import json
from transactions import Transaction
from jeniblock import JeniBlock
#from jenichain import JeniChain


class FileHandler:

    def save_jenichain(self, jenichain):
        try:
            with open("blockchain.txt", mode="w") as f:
                saveable_chain = [block.__dict__ for block
                                  in [JeniBlock(block_element.index,
                                                block_element.previous_hash,
                                                [transaction.__dict__ for transaction in block_element.transactions],
                                                block_element.proof,
                                                block_element.timestamp)
                                      for block_element in jenichain.chain]]

                f.write(json.dumps(saveable_chain))
                f.write("\n")
                saveable_transactions = [transaction.__dict__ for transaction in jenichain.open_transactions]
                f.write(json.dumps(saveable_transactions))
        except IOError:
            print("Savong failed!")

    def load_data(self, jenichain, open_transactions):
        try:
            with open("blockchain.txt", mode="r") as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_jenichain = []
                for block in blockchain:
                    previous_hash = block["previous_hash"]
                    index = block["index"]
                    proof = block["proof"]
                    timestamp = block["timestamp"]
                    transactions = [Transaction(transaction["sender"], transaction["recipient"], transaction["amount"])
                                    for transaction in block["transactions"]]

                    updated_block = JeniBlock(index, previous_hash, transactions, proof, timestamp)
                    updated_jenichain.append(updated_block)

                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for transaction in open_transactions:
                    updated_transaction = Transaction(transaction["sender"], transaction["recipient"], transaction["amount"])
                    updated_transactions.append(updated_transaction)

                jenichain = updated_jenichain
                open_transactions = updated_transactions
        except (IOError, IndexError):
            print("File not found: Make file")

        return jenichain, open_transactions

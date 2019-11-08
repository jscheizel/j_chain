import json
from transactions import Transaction
from jeniblock import JeniBlock


class FileHandler:

    @staticmethod
    def save_jenichain(jenichain):
        try:
            with open("blockchain-{}.txt".format(jenichain.port), mode="w") as f:
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

                f.write("\n")
                f.write(json.dumps(jenichain.get_peer_nodes()))
        except IOError:
            print("Saving failed!")

    @staticmethod
    def load_data(jenichain, open_transactions, peer_nodes, port):
        try:
            with open("blockchain-{}.txt".format(port), mode="r") as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_jenichain = []
                for block in blockchain:
                    previous_hash = block["previous_hash"]
                    index = block["index"]
                    proof = block["proof"]
                    timestamp = block["timestamp"]
                    transactions = [Transaction(transaction["sender"], transaction["recipient"], transaction["signature"], transaction["amount"])
                                    for transaction in block["transactions"]]

                    updated_block = JeniBlock(index, previous_hash, transactions, proof, timestamp)
                    updated_jenichain.append(updated_block)

                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for transaction in open_transactions:
                    updated_transaction = Transaction(transaction["sender"], transaction["recipient"],
                                                      transaction["signature"], transaction["amount"])
                    updated_transactions.append(updated_transaction)

                jenichain = updated_jenichain
                open_transactions = updated_transactions
                peer_nodes = set(json.loads(file_content[2]))

        except (IOError, IndexError):
            print("File not found: Make file")
            f = open("blockchain-{}.txt".format(port), mode="w+")
            f.close()

        return jenichain, open_transactions, peer_nodes

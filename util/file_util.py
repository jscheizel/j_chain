import json
from transactions import Transaction
from jblock import JBlock


class FileHandler:

    @staticmethod
    def save_j_chain(j_chain):
        try:
            with open("blockchain-{}.txt".format(j_chain.port), mode="w") as f:
                saveable_chain = [block.__dict__ for block
                                  in [JBlock(block_element.index,
                                             block_element.previous_hash,
                                             [transaction.__dict__ for transaction in block_element.transactions],
                                             block_element.proof,
                                             block_element.timestamp)
                                      for block_element in j_chain.chain]]

                f.write(json.dumps(saveable_chain))
                f.write("\n")

                saveable_transactions = [transaction.__dict__ for transaction in j_chain.open_transactions]
                f.write(json.dumps(saveable_transactions))

                f.write("\n")
                f.write(json.dumps(j_chain.get_peer_nodes()))
        except IOError:
            print("Saving failed!")

    @staticmethod
    def load_data(j_chain, open_transactions, peer_nodes, port):
        try:
            with open("blockchain-{}.txt".format(port), mode="r") as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_j_chain = []
                for block in blockchain:
                    previous_hash = block["previous_hash"]
                    index = block["index"]
                    proof = block["proof"]
                    timestamp = block["timestamp"]
                    transactions = [Transaction(transaction["sender"], transaction["recipient"], transaction["signature"], transaction["amount"])
                                    for transaction in block["transactions"]]

                    updated_block = JBlock(index, previous_hash, transactions, proof, timestamp)
                    updated_j_chain.append(updated_block)

                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for transaction in open_transactions:
                    updated_transaction = Transaction(transaction["sender"], transaction["recipient"],
                                                      transaction["signature"], transaction["amount"])
                    updated_transactions.append(updated_transaction)

                j_chain = updated_j_chain
                open_transactions = updated_transactions
                peer_nodes = set(json.loads(file_content[2]))

        except (IOError, IndexError):
            print("File not found: Make file")
            f = open("blockchain-{}.txt".format(port), mode="w+")
            f.close()

        return j_chain, open_transactions, peer_nodes

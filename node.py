from flask import Flask, jsonify, request, send_from_directory
from wallet import Wallet
from flask_cors import CORS
from j_chain import J_Chain


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def get_node_ui():
    return send_from_directory("ui", "node.html")


@app.route("/network", methods=["GET"])
def get_network_ui():
    return send_from_directory("ui", "network.html")


@app.route("/wallet", methods=["POST"])
def create_keys():
    wallet.create_keys()
    # participants.append(wallet.public_key)
    if wallet.save_keys():
        global j_chain
        j_chain = J_Chain(wallet.public_key, port)
        response = {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "funds": j_chain.get_balance(wallet.public_key)
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Saving the keys failed."
        }
        return jsonify(response), 500


@app.route("/wallet", methods=["GET"])
def load_keys():
    # participants.append(wallet.public_key)
    if wallet.load_key():
        global j_chain
        j_chain = J_Chain(wallet.public_key, port)
        response = {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "funds": j_chain.get_balance(wallet.public_key)
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Loading the keys failed."
        }
        return jsonify(response), 500


@app.route("/transaction", methods=["POST"])
def add_transaction():
    values = request.get_json()
    required_fields = ["recipient", "amount"]
    if not values or not all(field in values for field in required_fields):
        response = {
            "message": "Required data is missing, please add recipient and amount."
        }
        return jsonify(response), 400

    recipient = values["recipient"]
    amount = values["amount"]
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = j_chain.add_transaction(wallet.public_key, recipient, signature, amount)
    if success:
        response = {
            "message": "Transaction successfully added",
            "sender": wallet.public_key,
            "recipient": recipient,
            "amount": amount,
            "signature": signature,
            "funds": j_chain.get_balance(wallet.public_key)
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Adding the Transaction failed."
        }
        return jsonify(response), 500


@app.route("/balance", methods=["GET"])
def get_balance():
    balance = j_chain.get_balance(wallet.public_key)
    if balance is not None:
        response = {
            "message": "Balance fetched successfully",
            "balance": balance
        }
        return jsonify(response), 200
    else:
        response = {
            "message": "Loading balance failed.",
            "wallet_set_up": wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route("/resolve", methods=["POST"])
def resolve_conflicts():
    replaces = j_chain.resolve()
    if replaces:
        response = {"message": "Chain was replaced"}
    else:
        response = {"message": "Local chain kept"}
    return jsonify(response), 200


@app.route("/mine", methods=["POST"])
def mine():
    if j_chain.resolve_conflicts:
        response = {"message": "Resolfe conflicts first, block not added"}
        return jsonify(response), 409
    block = j_chain.mine_block()
    if block is not None:
        block_dict = block.__dict__.copy()
        block_dict["transactions"] = [transaction.__dict__ for transaction in block_dict["transactions"]]
        response = {
            "message": "Block added successfully",
            "block": block_dict,
            "funds": j_chain.get_balance(wallet.public_key)
        }
        return jsonify(response), 200
    else:
        response = {
            "message": "Adding block failed",
            "wallet": wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route("/chain", methods=["GET"])
def get_chain():
    chain = j_chain.chain
    chain_dict = [block.__dict__.copy() for block in chain]
    for block_dict in chain_dict:
        block_dict["transactions"] = [transaction.__dict__ for transaction in block_dict["transactions"]]
    return jsonify(chain_dict), 200


@app.route("/transactions", methods=["GET"])
def get_open_transactions():
    transactions = j_chain.open_transactions
    transactions_dict = [transaction.__dict__.copy() for transaction in transactions]
    return jsonify(transactions_dict), 200


@app.route("/node", methods=["POST"])
def add_node():
    values = request.get_json()
    required_fields = ["node"]
    if not values or not all(field in values for field in required_fields):
        response = {
            "message": "Required data is missing, please add node."
        }
        return jsonify(response), 400
    else:
        node = values["node"]
        j_chain.add_peer_node(node)
        response = {
            "message": "Node successfully added",
            "all_nodes": j_chain.get_peer_nodes()
        }
        return jsonify(response), 201


@app.route("/nodes", methods=["GET"])
def get_nodes():
    nodes = j_chain.get_peer_nodes()
    response = {
        "all_nodes": nodes
    }
    return jsonify(response), 200


@app.route("/node/<node_url>", methods=["DELETE"])
def remove_node(node_url):
    if node_url == "" or node_url is None:
        response = {
            "message": "Node not found"
        }
        return jsonify(response), 400
    else:
        j_chain.remove_peer_node(node_url)
        response = {
            "message": "Node removed",
            "all_nodes": j_chain.get_peer_nodes()
        }
        return jsonify(response), 200


@app.route("/broadcast-transaction", methods=["POST"])
def braodcast_transaction():
    values = request.get_json()
    if not values:
        response = {"message":"No data found"}
        return jsonify(response), 400
    required = {"sender", "recipient", "amount", "signature"}
    if not all(key in values for key in required):
        response = {"message": "Data is missing"}
        return jsonify(response), 400
    success = j_chain.add_transaction(values["sender"], values["recipient"], values["signature"], values["amount"], broadcast=True)
    if success:
        response = {
            "message": "Transaction successfully added",
            "sender": values["sender"],
            "recipient": values["recipient"],
            "amount": values["amount"],
            "signature": values["signature"]
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Adding the Transaction failed."
        }
        return jsonify(response), 500


@app.route("/broadcast-block", methods=["POST"])
def braodcast_block():
    values = request.get_json()
    if not values:
        response = {"message": "No data found"}
        return jsonify(response), 400
    if "block" not in values:
        response = {"message": "Data is missing"}
        return jsonify(response), 400
    block = values["block"]
    if block["index"] == j_chain.chain[-1].index +1:
        success = j_chain.add_block(block)
        if success:
            response = {"message": "Block added"}
            return jsonify(response), 201
        else:
            response = {"message": "Block invalid?"}
            return jsonify(response), 409
    elif block["index"] > j_chain.chain[-1].index +1:
        j_chain.resolve_conflicts = True
        response = {"message": "Blockchain seems to differ from local blockchain"}
        return jsonify(response), 200
    else:  # <
        response = {"message": "Blockchain is too short"}
        return jsonify(response), 409


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    j_chain = J_Chain(wallet.public_key, port)
    app.run(host="0.0.0.0", port=port)

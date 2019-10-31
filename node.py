from flask import Flask, jsonify
from wallet import Wallet
from flask_cors import CORS
from jenichain import JeniChain


app = Flask(__name__)
wallet = Wallet()
jenichain = JeniChain(wallet.public_key)
CORS(app)


@app.route("/", methods=["GET"])
def get_ui():
    return "This works"


@app.route("/chain", methods=["GET"])
def get_chain():
    chain = jenichain.chain
    chain_dict = [block.__dict__.copy() for block in chain]
    for block_dict in chain_dict:
        block_dict["transactions"] = [transaction.__dict__ for transaction in block_dict["transactions"]]
    return jsonify(chain_dict), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

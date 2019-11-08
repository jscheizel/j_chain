from Crypto.PublicKey import RSA
import Crypto.Random
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import binascii

class Wallet:

    def __init__(self, port):
        self.private_key = None
        self.public_key = None
        self.port = port

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    # TODO move to file util
    def save_keys(self):
        try:
            with open("wallet-{}.txt".format(self.port), mode="w") as f:
                f.write(self.public_key)
                f.write("\n")
                f.write(self.private_key)
                return True
        except IOError:
            print("saving keys failed")
            return False

    def load_key(self):
        try:
            with open("wallet-{}.txt".format(self.port), mode="r") as f:
                keys = f.readlines()
                self.public_key = keys[0][:-1]
                self.private_key = keys[1]
                return True
        except IOError:
            print("loading keys failed")
            return False

    @staticmethod
    def generate_keys():
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()

        private_key_ascii = binascii.hexlify(private_key.export_key(format="DER")).decode("ascii")
        public_key_ascii = binascii.hexlify(public_key.export_key(format="DER")).decode("ascii")
        return private_key_ascii, public_key_ascii

    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.import_key(binascii.unhexlify(self.private_key)))
        sha_hash = SHA256.new((str(sender) + str(recipient) + str(amount)).encode("utf8"))
        signature = signer.sign(sha_hash)
        return binascii.hexlify(signature).decode("ascii")

    @staticmethod
    def verify_signture(transaction):
        if transaction.sender == "MINING":
            return True
        public_key = RSA.import_key(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        sha_hash = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode("utf8"))
        return verifier.verify(sha_hash, binascii.unhexlify(transaction.signature))


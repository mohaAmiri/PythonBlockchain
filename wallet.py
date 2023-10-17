import binascii
import pickle

from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class Wallet:
    def __init__(self):
        self.public_key = None
        self.private_key = None

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.public_key = public_key
        self.private_key = private_key

    def generate_keys(self):
        private_key = RSA.generate(1024, Random.new().read)
        public_key = private_key.public_key()
        return (binascii.hexlify(private_key.export_key(format='DER')).decode('ascii'),
                binascii.hexlify(public_key.export_key(format='DER')).decode('ascii')
                )

    def save_keys(self):
        if self.public_key is not None and self.private_key is not None:
            try:
                with open('wallet.txt', mode='wb') as f:
                    data = {'public_key': self.public_key, 'private_key': self.private_key}
                    f.write(pickle.dumps(data))
                print('keys saved successfully!!!')
                return True
            except (IOError, IndexError):
                print("saving wallet failed!!!")
                return False

    def load_keys(self):
        try:
            with open('wallet.txt', mode='rb') as f:
                data = pickle.loads(f.read())
                self.private_key = data['private_key']
                self.public_key = data['public_key']
            return True
        except (IOError, IndexError):
            print("loading wallet failed!!!")
            return False

    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new(
            (str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(transaction.signature))

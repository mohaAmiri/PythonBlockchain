import binascii
import pickle

from Crypto import Random
from Crypto.PublicKey import RSA


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

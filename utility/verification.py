from utility.hash_utils import hash_block, hash_string_256
from wallet import Wallet


class Verification:
    @staticmethod
    def verify_transaction(transaction, get_balance):
        user_balance = get_balance(transaction.sender)
        if user_balance >= transaction.amount and Wallet.verify_transaction(transaction):
            return True
        else:
            print('not enough balance!!!')
            return False

    @staticmethod
    def verify_chain(blockchain):
        for index, block in enumerate(blockchain):
            if index == 0:
                continue
            if not blockchain[index].previous_hash == hash_block(blockchain[index - 1]):
                print('verify chain > previous_hash failed!!!')
                return False
            if not Verification.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('verify chain > valid_proof failed!!!')
                return False
            return True

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[0:2] == "00"

from block import Block
from transaction import Transaction
from utility.hash_utils import hash_block

MINING_REWARD = 10


class Blockchain:
    def __init__(self, public_key):
        genesis_block = Block(0, '', [])
        self.chain = [genesis_block]
        self.open_transaction = []
        self.public_key = public_key

    def add_transaction(self, sender, recipient, amount):
        transaction = Transaction(sender, recipient, amount)
        self.open_transaction.append(transaction)
        return True

    def mine_block(self):
        index = len(self.chain)
        previous_hash = hash_block(self.chain[-1])
        """ Add Reward """
        reward_transaction = Transaction('MINING', self.public_key, MINING_REWARD)
        copied_transaction = self.open_transaction[:]
        copied_transaction.append(reward_transaction)
        """ generate new block and add to chain """
        new_block = Block(index, previous_hash, copied_transaction)
        self.chain.append(new_block)
        self.open_transaction = []
        return True

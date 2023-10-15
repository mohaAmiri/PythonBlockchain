from functools import reduce

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
        self.get_balance()
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
        self.get_balance()
        return True

    def get_balance(self):
        participant = self.public_key
        """ calculate total sent amount """
        sent_chain_tx = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in
                         self.chain]
        sent_op_tx = [tx.amount for tx in self.open_transaction if tx.sender == participant]
        sent_chain_tx.append(sent_op_tx)
        total_sent = reduce(lambda s, i: s + sum(i) if len(i) > 0 else s + 0,
                            sent_chain_tx, 0)

        """ calculate total received amount """
        received_chain_tx = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in
                             self.chain]
        received_op_tx = [tx.amount for tx in self.open_transaction if tx.recipient == participant]
        received_chain_tx.append(received_op_tx)
        total_received = reduce(lambda s, i: s + sum(i) if len(i) > 0 else s + 0,
                                received_chain_tx, 0)

        return int(total_received - total_sent)

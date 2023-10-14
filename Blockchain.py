from block import Block
from transaction import Transaction


class Blockchain:
    def __init__(self):
        genesis_block = Block(0, '', [])
        self.chain = [genesis_block]
        self.open_transaction = []

    def add_transaction(self, sender, recipient, amount):
        transaction = Transaction(sender, recipient, amount)
        self.open_transaction.append(transaction)
        print(self.open_transaction)
        return True

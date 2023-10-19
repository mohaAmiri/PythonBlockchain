from functools import reduce
import pickle

import requests.exceptions

from block import Block
from transaction import Transaction
from utility.hash_utils import hash_block
from utility.verification import Verification
from wallet import Wallet

MINING_REWARD = 10


class Blockchain:
    def __init__(self, public_key, node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block]
        self.open_transaction = []
        self.public_key = public_key
        self.peer_nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()

    def add_transaction(self, sender, recipient, signature, amount, is_receiving=False):
        if self.public_key is None:
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.open_transaction.append(transaction)
            self.save_data()
            if not is_receiving:
                for node in self.peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url,
                                                 json={'sender': sender, 'recipient': recipient, 'amount': amount,
                                                       'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def mine_block(self):
        if self.public_key is None:
            return None
        index = len(self.chain)
        previous_hash = hash_block(self.chain[-1])

        """ check verify signature """
        copied_transaction = self.open_transaction[:]
        for tx in copied_transaction:
            if not Wallet.verify_transaction(tx):
                print('verify signature failed!!!')
                return None
        """ Add Reward """
        reward_transaction = Transaction('MINING', self.public_key, '', MINING_REWARD)
        copied_transaction.append(reward_transaction)
        """ add POW """
        proof = self.proof_of_work()
        """ generate new block and add to chain """
        new_block = Block(index, previous_hash, copied_transaction, proof)
        self.chain.append(new_block)
        self.open_transaction = []
        self.save_data()
        for node in self.peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = new_block.__dict__.copy()
            converted_block['transactions'] = [tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, need resolving')
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return new_block

    def add_block(self, block):
        transactions = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in
                        block['transactions']]
        # careful not to send reward transaction to valid proof => transactions[:-1]
        proof_is_valid = Verification.valid_proof(transactions[:-1], block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'],
                                block['timestamp'])
        self.chain.append(converted_block)
        # to remove transaction after mining it
        stored_transactions = self.open_transaction[:]
        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] \
                        and opentx.amount == itx['amount'] and opentx.signature == itx['signature']:
                    try:
                        self.open_transaction.remove(opentx)
                    except ValueError:
                        print('item was already removed')
        self.save_data()
        return True

    def get_balance(self, sender=None):
        if sender is None:
            participant = self.public_key
        else:
            participant = sender

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

    def proof_of_work(self):
        previous_hash = hash_block(self.chain[-1])
        proof = 0
        while not Verification.valid_proof(self.open_transaction, previous_hash, proof):
            proof += 1
        return proof

    def save_data(self):
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='wb') as file:
                data = {
                    'blockchain': self.chain,
                    'ot': self.open_transaction,
                    'peer_nodes': self.peer_nodes
                }
                file.write(pickle.dumps(data))
        except IOError:
            print('Saving blockchain failed!!!')

    def load_data(self):
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='rb') as file:
                context = pickle.loads(file.read())
                self.chain = context['blockchain']
                self.open_transaction = context['ot']
                self.peer_nodes = context['peer_nodes']
                print('Data successfully loaded!!!')
        except (IOError, IndexError):
            pass

    def add_peer_node(self, node):
        self.peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        self.peer_nodes.discard(node)  # discard will delete object if it exists and if not does nothing
        self.save_data()

    def get_peer_nodes(self):
        return list(self.peer_nodes)

    def resolve(self):
        winner_chain = self.chain
        replace = False
        for node in self.peer_nodes:
            url = 'http://{}/chain'.format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [Block(block['index'], block['previous_hash'],
                                    [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                                     for tx in block['transactions']],
                                    block['proof'],
                                    block['timestamp']
                                    ) for block in node_chain]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue

        self.resolve_conflicts = False
        self.chain = winner_chain
        if replace:
            self.open_transaction = []
        self.save_data()
        return replace

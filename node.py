from Blockchain import Blockchain
from block import Block
from utility.verification import Verification


class Node:
    def __init__(self):
        self.public_key = 'Mohammad'
        self.blockchain = Blockchain(self.public_key)

    @staticmethod
    def get_user_choice():
        user_input = input('Your choice: ')
        return user_input

    @staticmethod
    def get_transaction_value():
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Your transaction amount please: '))
        return tx_recipient, tx_amount

    def print_blockchain(self):
        for block in self.blockchain.chain:
            print(block)
            print('-' * 30)
        else:
            print('=' * 20)

    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print('=' * 30)
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain blocks')
            print('4: Check transaction validity')
            print('5: Create wallet')
            print('6: Load Wallet')
            print('7: save Wallet')
            print('q: Quit')
            user_choice = self.get_user_choice()
            print('=' * 30)

            if user_choice == '1':
                """ add transaction """
                tx_data = self.get_transaction_value()
                tx_recipient, tx_amount = tx_data
                if self.blockchain.add_transaction(self.public_key, tx_recipient, tx_amount):
                    print("transaction Added!!!!")
                else:
                    print("transaction failed!!!")

            elif user_choice == '2':
                """ Mining Blocks """
                if self.blockchain.mine_block():
                    print("Block Added!!!!")
                else:
                    print("Mining Block failed!!!")

            elif user_choice == '3':
                """ Print Blockchain """
                self.print_blockchain()

            elif user_choice == 'q':
                print("Exited!!!")
                break

            """ verify chain """
            if not Verification.verify_chain(self.blockchain):
                break

            """ print balance of user """
            print('Balance of {}: {}'.format(self.public_key, self.blockchain.get_balance()))


node = Node()
node.listen_for_input()

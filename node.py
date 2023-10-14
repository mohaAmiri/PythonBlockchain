from Blockchain import Blockchain


class Node:
    def __init__(self):
        self.blockchain = Blockchain()
        self.node_id = 'Mohammad'

    @staticmethod
    def get_user_choice():
        user_input = input('Your choice: ')
        return user_input

    @staticmethod
    def get_transaction_value():
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Your transaction amount please: '))
        return tx_recipient, tx_amount

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
                if self.blockchain.add_transaction(self.node_id, tx_recipient, tx_amount):
                    print("transaction Added!!!!")
                else:
                    print("transaction failed!!!")

            elif user_choice == 'q':
                print("Exited!!!")
                break


node = Node()
node.listen_for_input()

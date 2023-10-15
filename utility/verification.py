from utility.hash_utils import hash_block


class Verification:
    @staticmethod
    def verify_transaction(transaction, get_balance):
        user_balance = get_balance()
        if user_balance >= transaction.amount:
            return True
        else:
            print('not enough balance!!!')
            return False

    @staticmethod
    def verify_chain(blockchain):
        chain = blockchain.chain
        for index, block in enumerate(chain):
            if index == 0:
                continue
            if not chain[index].previous_hash == hash_block(chain[index - 1]):
                print('verify chain failed!!!')
                return False
            return True

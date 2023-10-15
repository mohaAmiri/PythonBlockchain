class Verification:
    @staticmethod
    def verify_transaction(transaction, get_balance):
        user_balance = get_balance()
        if user_balance >= transaction.amount:
            return True
        else:
            print('not enough balance!!!')
            return False

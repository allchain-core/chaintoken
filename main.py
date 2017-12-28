from chaintoken.wallet import Wallet
from chaintoken.wallet.token import Token


if __name__ == '__main__':
    wallet_1 = None
    password_1 = None
    wallet_2 = None
    password_2 = None

    with Token() as tok:
        print('Tokens left in system: {}'.format(tok.left_supply))
        print('Create wallets')
        with Wallet(genesis=True) as w:
            wallet_1 = w.address
            password_1 = w.password
            print('\tCreated new genesis wallet with balance {} tokens: {}'.format(tok.max_supply, wallet_1))

        with Wallet() as w:
            wallet_2 = w.address
            password_2 = w.password
            print('\tCreated new customer wallet with balance 0 tokens: {}'.format(wallet_2))

        print('Test payments')
        with Wallet(wallet_1, password_1) as w:
            print('\tSending 1000 tokens to {}'.format(wallet_2))
            w.send(wallet_2, 1000)

        print('Checking balances')
        with Wallet(wallet_1, password_1) as w:
            print('\tGenesis {}: {}'.format(wallet_1, w.get_balance()))
        with Wallet(wallet_2, password_2) as w:
            print('\tCustomer {}: {}'.format(wallet_2, w.get_balance()))

        print('Tokens left in system: {}'.format(tok.left_supply))

        print('Checking refund')
        with Wallet(wallet_2, password_2) as w:
            print('\tSending 1000 tokens back to genesis - {}'.format(wallet_1))
            w.send(wallet_1, 1000)

        print('Checking balances')
        with Wallet(wallet_1, password_1) as w:
            print('\tGenesis {}: {}'.format(wallet_1, w.get_balance()))
        with Wallet(wallet_2, password_2) as w:
            print('\tCustomer {}: {}'.format(wallet_2, w.get_balance()))

        print('Tokens left in system: {}'.format(tok.left_supply))
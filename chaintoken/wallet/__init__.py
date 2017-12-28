import uuid
import time
from hashlib import sha1, sha256
from chaintoken.wallet.token import Token
from chaintoken.database.client import Mongo
from chaintoken.settings import SECRET_KEY, ADDRESS_STARTSWITH, TRANSACTION_FEE, TRANSACTION_FEE_PERCENTS


class Wallet(object):
    """
    Token wallet object
    """
    class AuthFailed(Exception):
        pass

    class DoesNotExist(Exception):
        pass

    class InvalidAmount(Exception):
        pass

    class NotEnoughTokens(Exception):
        pass

    def __init__(self, address=None, key=None, genesis=False):
        """
        Initialize wallet operating session
        :param address:
        :param key:
        :param genesis:
        """
        super().__init__()
        self.db = None

        self.address = address
        self.password = key
        self.balance = 0
        self.genesis = genesis

    @property
    def access_key(self):
        """
        Generate access_key from wallet password
        :return:
        """
        key_hash = sha256()
        key_hash.update(self.password.encode())
        key_hash.update(ADDRESS_STARTSWITH.encode())
        return key_hash.hexdigest()

    def __enter__(self):
        """
        Initialize session
        :return:
        """
        # Connect to database
        self.db = Mongo()

        # Authenticate wallet
        if self.address is None:
            wallet = self.generate()
            self.address = wallet['address']
            self.password = wallet['password']

            self.create()

        wallet = self.authenticate()
        if not wallet:
            raise Wallet.AuthFailed('Wrong address or password')

        # Cache properties
        self.balance = wallet['balance']
        self.genesis = wallet['genesis']

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit session
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        pass

    def get_balance(self):
        """
        Get balance
        :return:
        """
        self.balance = self.authenticate()['balance']
        return self.balance

    def transactions(self, offset=0, limit=100):
        """
        Receive latest transactions
        :param offset:
        :param limit:
        :return:
        """
        return self.db.transactions.find({
            '$or': [
                {'target': self.address},
                {'source': self.address}
            ]
        }).sort('created', -1).skip(offset).limit(limit)

    def send(self, address, amount):
        """
        Send tokens
        :param address:
        :param amount:
        :return:
        """
        with Token() as tok:
            # Validate amount
            try:
                amount = float(amount)
            except:
                raise Wallet.InvalidAmount('Invalid amount to be spent')

            if amount < 0:
                raise Wallet.InvalidAmount('Amount should be > 0')

            # Calculate substract amount
            subamount = amount + self.calculate_fee(amount)

            # Check balance
            if self.get_balance() < subamount and not self.genesis:
                raise Wallet.NotEnoughTokens('You don\'t have enough tokens to send')

            # Check if genesis wallet have no tokens left
            if tok.left_supply < subamount and self.genesis:
                raise Wallet.NotEnoughTokens('You don\'t have enough tokens to send')

            # Get target wallet
            wallet = self.db.wallets.find_one({'address': address})
            if not wallet:
                raise Wallet.DoesNotExist('Wrong target address')

            # Update source wallet
            if not self.genesis:
                self.db.wallets.update_one({'address': self.address}, {'$set': {'balance': self.balance-subamount}})

            # Update target wallet
            if not wallet['genesis']:
                self.db.wallets.update_one({'address': wallet['address']}, {'$set': {'balance': wallet['balance']+amount}})

            # Create transaction
            self.db.transactions.insert_one({
                'created': time.time(),
                'target': wallet['address'],
                'source': self.address,
                'amount': amount,
                'fee': subamount - amount
            })

            return True

    def authenticate(self):
        """
        Authenticate wallet
        :return:
        """
        return self.db.wallets.find_one({
            'address': self.address,
            'password': self.access_key
        })

    def create(self):
        """
        Save current wallet into db
        :return:
        """
        self.db.wallets.insert_one({
            'address': self.address,
            'password': self.access_key,
            'balance': 0.0,
            'genesis': self.genesis
        })

    def generate(self):
        """
        Generate new wallet
        :return:
        """
        uid = str(uuid.uuid4()).encode()
        address_hash = sha1()
        password_hash = sha256()

        # Generate address
        address_hash.update(uid)
        address_hash.update(SECRET_KEY.encode())
        address = '%s.%s' % (ADDRESS_STARTSWITH, address_hash.hexdigest()[:16])

        # Generate password
        password_hash.update(uid)
        password_hash.update(address.encode())
        password_hash.update(SECRET_KEY.encode())
        password = password_hash.hexdigest()

        return {
            'address': address,
            'password': password
        }

    @staticmethod
    def calculate_fee(amount):
        """
        Calculate and return fee amount
        :param amount:
        :return:
        """
        if TRANSACTION_FEE_PERCENTS:
            return amount * TRANSACTION_FEE
        return TRANSACTION_FEE

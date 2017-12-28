from chaintoken.database.client import Mongo
from chaintoken.settings import MAX_TOKENS_SUPPLY


class Token(object):
    """
    Token manager
    """
    def __init__(self):
        """
        Initialize token manager
        """
        super().__init__()
        self.db = None

    def __enter__(self):
        # Connect to database
        self.db = Mongo()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def part_balance(self, address):
        """
        Percent tokens from total amount.
        :param address:
        :return:
        """
        return float(self.get_balance(address) or 0) / self.total_supply * 100

    def get_balance(self, address):
        """
        Returns balance
        :param address:
        :return:
        """
        wallet = self.db.wallets.find_one({'address': address})
        if not wallet:
            return None

        return wallet['balance']

    @property
    def max_supply(self):
        """
        Returns maximal supply
        :return:
        """
        return MAX_TOKENS_SUPPLY

    @property
    def left_supply(self):
        """
        Tokens left supply
        :return:
        """
        return self.max_supply - self.total_supply

    @property
    def total_supply(self):
        """
        Returns total supply
        :param Mongo db:
        :return:
        """
        result = list(self.db.wallets.aggregate([
            {'$group': {
                '_id': None,
                'total_supply': {'$sum': '$balance'}
            }}
        ]))

        return result[0]['total_supply'] if result else 0


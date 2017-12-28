from pymongo import MongoClient
from chaintoken.settings import MONGO
from urllib.parse import quote_plus


class Mongo(object):
    __connections__ = dict()

    def __init__(self):
        super().__init__()
        self.db = Mongo.connect(**MONGO)

    @property
    def wallets(self):
        return self.db.wallets

    @property
    def transactions(self):
        return self.db.transactions

    @staticmethod
    def connect(host, port=27017, db='tokens', user=None, password=None):
        if user is not None:
            dsn = 'mongodb://%s:%s@%s:%d' % (quote_plus(user), quote_plus(password), host, port)
        else:
            dsn = 'mongodb://%s:%d' % (host, port)

        if dsn not in Mongo.__connections__:
            Mongo.__connections__[dsn] = MongoClient(dsn)[db]

        return Mongo.__connections__.get(dsn)


__all__ = ['Mongo']

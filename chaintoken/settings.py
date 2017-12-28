# Copyright (c) Allchain.io 2017


# MongoDB Configuration
# https://www.mongodb.com/
MONGO = dict(
    host='127.0.0.1',
    port=27017,
    db='allchain',
    user=None,
    password=None
)


# Maximal tokens supply
# 0 - unlimited
MAX_TOKENS_SUPPLY = pow(10, 12)


# Secret key to be used as salt for address keys
SECRET_KEY = ''


# Address should starts with
ADDRESS_STARTSWITH = 'acn'


# Transaction fee settings
# If TRANSACTION_FEE_PERCENTS is set to True, then all
# transactions fees amount will be calculated as percents
#
#  TRANSACTION_FEE_PERCENTS = True
#  TRANSACTION_FEE = 0.05  - 5%
#
# if disabled
#
#  TRANSACTION_FEE_PERCENTS = False
#  TRANSACTION_FEE = 0.05  - 0.05 tokens
#
# fee will be substracted from sender
TRANSACTION_FEE_PERCENTS = False
TRANSACTION_FEE = 0.0

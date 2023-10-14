import json
from hashlib import sha256


def hash_string_256(string):
    """ generate hash """
    return sha256(string).hexdigest()


def hash_block(block):
    """ block is a class object and should be converted to json string to generate hash """
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())

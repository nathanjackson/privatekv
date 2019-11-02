#!/usr/bin/env python3

import pickle

from pyoram.oblivious_storage.tree.path_oram import PathORAM

class KeyNotFoundError(Exception):
    """Raised whenever a key was not found in a KV Store."""
    def __init__(self, key):
        self.key = key
        super(KeyNotFoundError, self).__init__("Key \"%s\" not found" % (key))

class KVORAM(object):
    """
    KVORAM objects wrap a PathORAM object. KVORAM acts as an abstraction layer
    to provide the user with an easy to use key-value inteface.

    Each block in the ORAM holds one value. The block ID is computed using the
    Python hash function. As of Python 3.3, the hash is salted with a random
    seed. To be able to use this class, you MUST set the "PYTHONHASHSEED"
    environment variable.
    """
    def __init__(self, oram):
        """
        Setup a PathORAM backend given the PathORAM object.
        :oram: the ORAM object
        """
        self.oram = oram

    def put(self, key, val):
        """
        Insert or update a key-value pair into the ORAM.
        :key: the key
        :val: the value
        """
        # First compute the hash of the key and block where the data will be
        # stored.
        h = hash(key)
        block_id = h % self.oram.block_count
        # Serialize the data and pad to the block size.
        serialized = pickle.dumps(val)
        serialized += b"\x00" * (self.oram.block_size - len(serialized))
        # Write the data.
        self.oram.write_block(block_id, bytes(serialized))

    def get(self, key):
        """
        Retrieves the value for the given key from ORAM.
        :key: the key
        """
        # Compute the hash of the key and block where to look for data.
        h = hash(key)
        block_id = h % self.oram.block_count
        # Read the data from the block.
        data = self.oram.read_block(block_id)
        # Attempt to deserialize.
        try:
            return pickle.loads(data)
        except pickle.UnpicklingError as e:
            raise KeyNotFoundError(key) from e

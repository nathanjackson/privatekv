#!/usr/bin/env python3

""" This script is used to initialize the data store on the server. """

import pickle

import paramiko

from argparse import ArgumentParser
from tempfile import NamedTemporaryFile

from pyoram.oblivious_storage.tree.path_oram import PathORAM

BLOCK_SIZE = 4096
BLOCK_COUNT = 2 ** (8+1) - 1

ap = ArgumentParser(
    description="initialize a Path ORAM and store it on a SFTP server")
ap.add_argument("storename", help="the store name")
ap.add_argument("host", help="the host name")
ap.add_argument("user", help="the user name")
ap.add_argument("key", help="RSA private key file")
ap.add_argument("--port", "-p", default=22)
args = ap.parse_args()

print("Building ORAM...")
with NamedTemporaryFile(delete=False) as tmp:
    tmpname = tmp.name

oram = PathORAM.setup(tmpname,
                      BLOCK_SIZE,
                      BLOCK_COUNT,
                      storage_type="file",
                      ignore_existing=True)
oram.close()

keyfile_name = "%s.key" % (args.storename)
stashfile_name = "%s.stash" % (args.storename)
positionfile_name = "%s.position" % (args.storename)

with open(keyfile_name, "wb") as keyfile:
    keyfile.write(oram.key)
with open(stashfile_name, "wb") as stashfile:
    pickle.dump(oram.stash, stashfile)
with open(positionfile_name, "wb") as positionfile:
    pickle.dump(oram.position_map, positionfile)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
rsa_key = paramiko.RSAKey.from_private_key_file(args.key)

ssh.connect(args.host,
            port=args.port,
            username=args.user,
            pkey=rsa_key)
sftp = ssh.open_sftp()
sftp.put(tmpname, args.storename)
sftp.close()
ssh.close()

print("\nORAM Initialized.")
print("The following files must be retained client side - DO NOT LOSE THEM\n")
print("  %s\n  %s\n  %s\n" %(keyfile_name, stashfile_name, positionfile_name))

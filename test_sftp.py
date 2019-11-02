#!/usr/bin/env python3

import multiprocessing
import pickle

import paramiko

from argparse import ArgumentParser
from tempfile import NamedTemporaryFile

from pyoram.oblivious_storage.tree.path_oram import PathORAM

BLOCK_SIZE = 4096
BLOCK_COUNT = 2 ** (8+1) - 1

ap = ArgumentParser(
    description="test Path ORAM on the SFTP server")
ap.add_argument("storename", help="the store name")
ap.add_argument("host", help="the host name")
ap.add_argument("user", help="the user name")
ap.add_argument("key", help="RSA private key file")
ap.add_argument("--port", "-p", default=22)
args = ap.parse_args()

keyfile_name = "%s.key" % (args.storename)
stashfile_name = "%s.stash" % (args.storename)
positionfile_name = "%s.position" % (args.storename)

with open(keyfile_name, "rb") as keyfile:
    key = keyfile.read()
with open(stashfile_name, "rb") as stashfile:
    stash = pickle.load(stashfile)
with open(positionfile_name, "rb") as positionfile:
    position_map = pickle.load(positionfile)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
rsa_key = paramiko.RSAKey.from_private_key_file(args.key)

ssh.connect(args.host,
            port=args.port,
            username=args.user,
            pkey=rsa_key)
sftp = ssh.open_sftp()

with PathORAM(args.storename,
              stash,
              position_map,
              key=key,
              storage_type="sftp",
              cached_levels=6,
              concurrency_level=1,
              sshclient=ssh) as oram:
    oram.read_block(0)

sftp.close()
ssh.close()

#!/usr/bin/env python3

from privatekv.store import KVORAM

kv = KVORAM.setup("test5", "localhost", "pkv", "pkv_test", port=41657)

print(kv.get(3))

kv.close()

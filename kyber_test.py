import unittest

import secrets

from kyber import genkey, encrypt, decrypt


class kyber_pke_test(unittest.TestCase):
    def test_gen_enc_dec(self):
        d = secrets.token_bytes(32)
        r = secrets.token_bytes(32)
        msg = [secrets.randbits(1) for _ in range(256)]

        pub, prv = genkey(d)
        ct = encrypt(pub, msg, r)
        dec = decrypt(prv, ct)
        self.assertEqual(dec, msg)

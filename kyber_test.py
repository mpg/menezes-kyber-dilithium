import unittest

import secrets

from kyber import KyberPKE


class KyberPKETest(unittest.TestCase):
    def test_rand_gen_enc_dec(self):
        d = secrets.token_bytes(32)
        r = secrets.token_bytes(32)
        msg = secrets.token_bytes(32)

        for s in 512, 768, 1024:
            pke = KyberPKE(s)

            pub, prv = pke.genkey(d)
            ct = pke.encrypt(pub, msg, r)
            dec = pke.decrypt(prv, ct)

            self.assertEqual(dec, msg)

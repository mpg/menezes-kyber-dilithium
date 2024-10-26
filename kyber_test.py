import unittest

from random import randint

from kyber import genkey, encrypt, decrypt


class kyber_pke_test(unittest.TestCase):
    def test_gen_enc_dec(self):
        pub, prv = genkey()
        msg = [randint(0, 1) for _ in range(256)]
        ct = encrypt(pub, msg)
        dec = decrypt(prv, ct)
        self.assertEqual(dec, msg)

import unittest

import secrets

from kyber import KyberPKE


class KyberPKETest(unittest.TestCase):
    def test_rand_gen_enc_dec_and_sizes(self):
        d = secrets.token_bytes(32)
        r = secrets.token_bytes(32)
        msg = secrets.token_bytes(32)

        # Size -> encryption key len, decryption key len, ciphertext len,
        #
        # For the first and last colum (encryption key, ciphertext), use
        # Table 3 Sizes (in bytes) of keys and ciphertexts of ML-KEM, p. 39.
        #
        # But encryption key (PKE) differs from decapsulation key (KEM).
        # So here use 384 * k (dk_PKE input of Algorithm 15 K-PKE.Decrypt).
        sizes = {
            512: (800, 384 * 2, 768),
            768: (1184, 384 * 3, 1088),
            1024: (1568, 384 * 4, 1568),
        }

        for s in 512, 768, 1024:
            pke = KyberPKE(s)

            pub, prv = pke.genkey(d)
            ct = pke.encrypt(pub, msg, r)
            dec = pke.decrypt(prv, ct)

            self.assertEqual(dec, msg)

            ek_len, dk_len, ct_len = sizes[s]
            self.assertEqual(len(pub), ek_len)
            self.assertEqual(len(prv), dk_len)
            self.assertEqual(len(ct), ct_len)

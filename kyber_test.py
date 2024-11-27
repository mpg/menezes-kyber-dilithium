import unittest

import secrets

from kyber import KyberPKE, KyberKEM


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

            pub, prv = pke.keygen(d)
            ct = pke.encrypt(pub, msg, r)
            dec = pke.decrypt(prv, ct)

            self.assertEqual(dec, msg)

            ek_len, dk_len, ct_len = sizes[s]
            self.assertEqual(len(pub), ek_len)
            self.assertEqual(len(prv), dk_len)
            self.assertEqual(len(ct), ct_len)


class KyberKEMTest(unittest.TestCase):
    def test_rand_gen_enc_dec_and_sizes(self):
        # Table 3 Sizes (in bytes) of keys and ciphertexts of ML-KEM, p. 39.
        sizes = {
            512: (800, 1632, 768),
            768: (1184, 2400, 1088),
            1024: (1568, 3168, 1568),
        }

        for s in 512, 768, 1024:
            kem = KyberKEM(s)

            ek, dk = kem.keygen()
            K, c = kem.encaps(ek)
            K_prime = kem.decaps(dk, c)

            self.assertEqual(K, K_prime)

            ek_len, dk_len, c_len = sizes[s]
            self.assertEqual(len(ek), ek_len)
            self.assertEqual(len(dk), dk_len)
            self.assertEqual(len(c), c_len)

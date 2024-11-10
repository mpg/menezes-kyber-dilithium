Code written while following https://cryptography101.ca/kyber-dilithium/

This is for my own fun/education, but I'm sharing in case other people might
enjoy it and/or find it educative too.

If you want to read this code while following the course, I'd recommend going
through the history (commit messages often mention slide numbers which should
make it easy to map a lecture to a set of commits). IMO one of the great
strengths of the course is the way things are built gradually, so if this code
is used as a complement, if should probably be read in a gradual way as well.

Links about Kyber (ML-KEM)
==========================

Spec, original paper & submission packages:
- https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf
- https://pq-crystals.org/kyber/resources.shtml

Implementations:
- https://pq-crystals.org/kyber/software.shtml
- https://github.com/PQClean/PQClean
- https://github.com/mupq
- https://github.com/RustCrypto/KEMs/tree/master/ml-kem

Test vectors:
- https://github.com/C2SP/CCTV/tree/main/ML-KEM (some of the files (under CC0) copied here)
- https://github.com/usnistgov/ACVP-Server/tree/master/gen-val/json-files/ML-KEM-keyGen-FIPS203
- https://github.com/usnistgov/ACVP-Server/tree/master/gen-val/json-files/ML-KEM-encapDecap-FIPS203

Misc:
- https://words.filippo.io/dispatches/kyber-math/

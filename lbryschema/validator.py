import ecdsa
import hashlib
from lbryschema.schema import NIST256p, NIST384p, SECP256k1


def validate_claim_id(claim_id):
    hex_chars = "0123456789abcdefABCDEF"
    assert len(claim_id) == 64, "Incorrect claimid length: %i" % len(claim_id)
    for c in claim_id:
        assert c in hex_chars, "Claim id is not hex encoded"


class Validator(object):
    HASHFUNC = None

    def __init__(self, public_key, certificate_claim_id):
        if not isinstance(public_key, ecdsa.VerifyingKey):
            raise Exception("Key is not type needed for verification")
        self._public_key = public_key
        self._certificate_claim_id = certificate_claim_id

    @property
    def public_key(self):
        return self._public_key

    @property
    def certificate_claim_id(self):
        return self._certificate_claim_id

    @staticmethod
    def key_from_der(der):
        return ecdsa.VerifyingKey.from_der(der)

    @classmethod
    def load_from_certificate(cls, certificate_claim, certificate_claim_id):
        certificate = certificate_claim.certificate
        return cls(cls.key_from_der(certificate.publicKey), certificate_claim_id)

    def validate_signature(self, digest, signature):
        return self.public_key.verify_digest(signature, digest)

    def validate_claim_signature(self, claim, claim_id):
        # check that the claim ids provided are the 64 characters long and hex encoded
        validate_claim_id(claim_id)

        # extract and serialize the stream from the claim, then check the signature

        publisher_signature = claim['publisherSignature']['signature']

        to_sign = "%s%s%s" % (claim_id.decode('hex'),
                              claim.serialized_no_signature,
                              self.certificate_claim_id.decode('hex'))

        return self.validate_signature(self.HASHFUNC(to_sign).digest(), publisher_signature)


class NIST256pValidator(Validator):
    HASHFUNC = hashlib.sha256


class NIST384pValidator(Validator):
    HASHFUNC = hashlib.sha384


class SECP256k1Validator(Validator):
    HASHFUNC = hashlib.sha256


def get_validator(curve):
    if curve == NIST256p:
        return NIST256pValidator
    elif curve == NIST384p:
        return NIST384pValidator
    elif curve == SECP256k1:
        return SECP256k1Validator
    else:
        raise Exception("Unknown curve: %s" % str(curve))

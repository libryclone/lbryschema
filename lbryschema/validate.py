from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from lbryschema.schema.claim import Claim


def _unpack_sig(sig_bytes):
    cnt = 0
    total = 0
    while sig_bytes:
        total += sig_bytes.pop() * (256 ** cnt)
        cnt += 1
    return (total, )


def validate_signed_stream_claim(claim, cert):
    # check pub key hashes match
    stream_pub_key_hash = claim.publisher_signature.signature.public_key_hash
    cert_pub_key_hash = cert.public_key.public_key_hash
    if not stream_pub_key_hash == cert_pub_key_hash:
        return False

    # check that the public key hash is actually the hash of the public key
    cert_public_key = cert.public_key.public_key
    key_hash = SHA256.new(cert_public_key).digest()
    if not key_hash == stream_pub_key_hash:
        return False

    # extract and serialize the stream from the claim, then check the signature
    key = RSA.importKey(cert_public_key)
    stream = claim.stream
    publisher_signature = bytearray(claim.publisher_signature.signature.signature)
    _temp_claim_dict = {
        "version": "_0_0_1",
        "stream": stream
    }
    _temp_claim = Claim.load(_temp_claim_dict)
    msg = _temp_claim.SerializeToString()
    return key.verify(msg, _unpack_sig(publisher_signature[::-1]))

import os, json
from base64 import b64encode, b64decode

import hmac
import hashlib

import Crypto.Hash.SHA256 as SHA256
import Crypto.PublicKey.RSA as RSA
from Crypto.Signature import PKCS1_v1_5


cwd = os.path.dirname(os.path.abspath(__file__))
private_key_file = os.path.join(cwd, '..', 'private.pem')
public_key_file = os.path.join(cwd, '..', 'public.pem')

with open(private_key_file, 'r') as keyfile:
    private_key = keyfile.read()

with open(public_key_file, 'r') as keyfile:
    public_key = keyfile.read()

shared_key = b64encode(os.urandom(32)).decode()

### CONFIG - START ###

### For use with RSA:
algorithm = 'rsa'
sign_key = private_key
verify_key = public_key

### For use with SHA256:
# algorithm = 'sha256'
# sign_key = shared_key
# verify_key = shared_key

### CONFIG - END ###

def hashit(value):
    h = SHA256.new(value)
    return h

def _sign(algorithm, key, message):
    if algorithm == 'rsa':
        signer = PKCS1_v1_5.new(RSA.importKey(key))
        signature = signer.sign(hashit(message))
        return b64encode(signature)

    elif algorithm == 'sha256':
        return b64encode(hmac.new(key.encode(), message, hashlib.sha256).digest())
    
    raise ValueError("Only rsa and sha256 supported.")

def _verify(algorithm, key, data, signature):
    if algorithm == 'rsa':
        signer = PKCS1_v1_5.new(RSA.importKey(key).publickey())
        return signer.verify(hashit(data.encode()), b64decode(signature))

    elif algorithm == 'sha256':
        our_sign = b64encode(hmac.new(key.encode(), data.encode(), hashlib.sha256).digest())
        return our_sign.decode() == signature

def sign(message):
    data = json.dumps(message).encode()
    signature = _sign(algorithm, sign_key, data)
    return b64encode( algorithm.encode() + b":" + signature + b":" + data ).decode()

def verify(data):
    algorithm, signature, message = b64decode(data).decode().split(":", 2)
    okay = _verify(algorithm, verify_key, message, signature)
    if okay:
        return json.loads(message)
    
    raise ValueError("INVALID SIGNATUER!1!")

if __name__ == '__main__':
    # Give test values if file is run directly.

    value = {'id': 48, 'user': 'someone', 'role': 'user'}
    cookie = sign(value)
    print("cookie: %r" % cookie)

    verified = verify(cookie)
    print("verified: %r" % verified)


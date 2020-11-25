import base64
import binascii
import hashlib
import os


def generate_password():
    return base64.b64encode(os.urandom(10)).decode()[-10:-2]

def generate_user_session_token():
    token = binascii.hexlify(os.urandom(32))
    hashed_token = hashlib.sha256(token).hexdigest()

    return token, hashed_token

import iota
import json
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from cliota.seedgen import gen_seed


class WalletEncryption:
    def encrypt(self, data, password):
        if isinstance(data, str):
            data = bytes(data, 'utf-8')

        salt = bytes(os.urandom(16))
        kdf = self._get_kdf(salt)

        key = base64.urlsafe_b64encode(kdf.derive(bytes(password, 'utf-8')))
        f = Fernet(key)
        return salt + base64.urlsafe_b64decode(f.encrypt(data))

    def decrypt(self, data, password):
        salt = data[:16]
        token = data[16:]

        kdf = self._get_kdf(salt)

        key = base64.urlsafe_b64encode(kdf.derive(bytes(password, 'utf-8')))
        f = Fernet(key)

        return f.decrypt(base64.urlsafe_b64encode(token))

    def _get_kdf(self, salt):
        return PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )


class WalletFile:
    def __init__(self, wfile, password, encryptor=WalletEncryption(),
                 seed=None):
        self.wfile = wfile
        self.password = password
        self.encryptor = encryptor

        if os.path.isfile(wfile):
            data = self.encryptor.decrypt(open(wfile, 'rb').read(), password)
            fobj = json.loads(data)
            self.addresses = fobj['addresses']
            self.seed = fobj['seed']
        else:
            # {address, balance, txs}
            self.addresses = []
            self.seed = seed if seed else gen_seed()

    def save(self):
        objstr = json.dumps({
            'addresses': self.addresses,
            'seed': self.seed
        })

        encrypted = self.encryptor.encrypt(objstr, self.password)
        with open(self.wfile, 'wb') as fh:
            fh.write(encrypted)

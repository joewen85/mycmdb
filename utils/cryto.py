# -*- coding: utf-8 -*-
# @Time     : 2020/5/26 11:03 AM
# @Author   : Joe
# @Site     :
# @File     : cryto.py
# @Software : PyCharm
# @function : RSA encrypt & decrypt

import binascii
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5
try:
    from config import Config as CONFIG
except ImportError:
    msg = """

        Error: No config file found.

        You can run `cp config_example.py config.py`, and edit it.
        """
    raise ImportError(msg)


class RsaCrypto(object):
    """RSA加密"""
    def __init__(self):
        self.public_key = CONFIG.PUBLIC_KEY
        self.private_key = CONFIG.PRIVATE_KEY

    def encrypt(self, plaintext):
        """加密"""
        try:
            recipient_key = RSA.import_key(self.public_key)
            cipher_rsa = PKCS1_v1_5.new(recipient_key)

            en_data = cipher_rsa.encrypt(plaintext.encode('utf-8'))
            hex_data = binascii.hexlify(en_data).decode('utf-8')

            return {'state': 1, 'message': hex_data}
        except Exception as err:
            return {'state': 0, 'message': str(err)}

    def decrypt(self, hex_data):
        """解密"""
        try:
            private_key = RSA.import_key(self.private_key)
            cipher_rsa = PKCS1_v1_5.new(private_key)

            en_data = binascii.unhexlify(hex_data.encode('utf-8'))
            data = cipher_rsa.decrypt(en_data, None).decode('utf-8')

            return {'state': 1, 'message': data}
        except Exception as err:
            return {'state': 0, 'message': str(err)}


# if __name__ == '__main__':
#     data = (RsaCrypto().encrypt('Asking168'))
#     print(len(data['message']))
    # print(RsaCrypto().decrypt('2e3df74012856adeb9ab4197502cbaf02e5126ddd7eb199f289291499db030b19e961b836c0045718d25fa0e00c70240634c6cc7bc4f9115919a3b4bdc6883bf192d88a8e01baa3e5af0d783c5d493408e0cb75f01b78087fac3f9473763f83e8c6e4176ab8c0a881b0c6bc5079a6bb72c693a42d7775a616a596aeac6d0bdc021ee5064be4da2f2ec6d0a1c56d42ab16d51c99d47c5cb60286cc7c886fa1006b32df8fdb0950dfb6d27ac428e2f7a107e81453354589875de69b78e8508eb598d5924bac5dd7b91e57439b28fa44b0278e295511212af114cc8b4720054ff88e2fc957c67e0d1dda7f896c699b2275f303204d8c2e1d19cd247cdeeca420cb0'))


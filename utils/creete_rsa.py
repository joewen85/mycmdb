# -*- coding: utf-8 -*-
# @Time     : 2019/12/17 3:00 PM
# @Author   : Joe
# @Site     :
# @File     : create_key.py
# @Software : PyCharm
# @function : create RSA key


from Cryptodome.PublicKey import RSA

def create_rsa_key():
    """生成RSA key"""
    try:
        # 选择秘钥位数，位数越高越安全，同时加密速度也越慢
        key = RSA.generate(2048)
        encrypted_key = key.export_key(pkcs=8)
        public_key = key.publickey().exportKey().decode('utf-8')
        private_key = encrypted_key.decode('utf-8')
        return {'state': 1, 'message':{'public_key': public_key, 'private_key': private_key}}
    except Exception as err:
        return {'state': 0, 'message': str(err)}


if __name__ == '__main__':
    print(create_rsa_key())

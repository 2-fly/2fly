#!/usr/bin/env python
# -*- coding:utf-8 -*-



from binascii import b2a_hex, a2b_hex

#easy_install PyCrypto
from Crypto.Cipher import DES



class MyCrypto(object):
    """ key must be 8 bytes """
    def __init__(self, key='bestiamp'):
        self.key = key
        self.padding = '\x00'
        self.cryptor = DES.new(self.key)

    def encode(self, text):
        length = 8

        count = len(text)
        if count < length:
            add = length - count
            text += self.padding*add
        elif count > length:
            add = (length - (count%length))
            text += self.padding*add

        return b2a_hex(self.cryptor.encrypt(text))

    def decode(self, s):
        content = a2b_hex(s)
        text = self.cryptor.decrypt(content)
        text = text.rstrip(self.padding)
        return text

if __name__ == '__main__':
    key = 'bestiamp'
    data =  '{"a": "123中文", sss}'
    ec = MyCrypto(key)
    ed = ec.encode(data)
    dd = ec.decode(ed)

    assert dd == data

    ec = MyCrypto(key)
    s = 'a=1&b=2&c=3'
    ed = ec.encode(s)
    print ed
    print ec.decode(ed)
    print len(ed)
    print len(s)


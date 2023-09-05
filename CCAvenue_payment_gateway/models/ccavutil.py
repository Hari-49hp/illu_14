#!/usr/bin/env python

from Crypto.Cipher import AES
import hashlib

def pad(data):
    length = 16 - (len(data) % 16)
    data += chr(length)*length
    return data

def encrypt(plainText,workingKey):
        iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        plainText = pad(plainText)
        encDigest = hashlib.md5()
        encDigest.update(workingKey.encode())
        enc_cipher = AES.new(encDigest.digest(), AES.MODE_CBC, iv)
        encryptedText = enc_cipher.encrypt(plainText.encode("utf-8")).encode('hex')
        return encryptedText



def decrypt(cipherText,workingKey):
    iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'

    print(cipherText)
    decDigest = hashlib.md5()
    decDigest.update(workingKey.encode())
    encryptedText = cipherText
    dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
    decryptedText = dec_cipher.decrypt(encryptedText)
    return decryptedText


decrytext = "8d764acb14f9b02e163365b4795d54abe4747d8f91dd9804bf506dfbdec80d428369c2caee2e56c9e9be98e5df14553b827296bc56f0156791cf82a910f0e5f6fa2c1f56ef929f8e8d527c2918fd8791efe5afaa44c1879601588a99614513233d1953e25bedad95a309d844617c3d3b8635a59d2fa4a821f3ad4ef2779efc5ec96aac9bdca554d971ec727458d4c7175ed982da014872e98eade2bfc275ce10ca77158db92e1aed82510061fec77e2c0e247ccb5c95972508bc488d9e3b9bae1b4753abe60ef4e21adcc7e085ebc2baf2acd7cba66e51689d160358843089ad7823fe6237130149be590a8c73b31d43988b6068116e350b57a3a5600e6022b88dfbe6bfc442d9ecc8ccd138642d2fc5d9e67e9332b229df684d19c70201fa157e5b58ee4e156b6442c3b12cb5eec782590afc2658e846405f2db976f194b612a8f875d346b419c1209db4f79b48b89ca4c3e2155928feeb4886a880dfea2cc49b5f654f9ab92e0a51295dd596698bea336b06e7c00363915626065f558379208d13dbcc404b27e4b154ba344a3cc0fce2fdef3d1b4f30cfe00d4eaa05478c1ba8798ad3b79948446234a9f03c32e3bbd560e7252d0ddb4f9e59361e3bb981162bcc546e137af1d4484334c2247333aa3859e83fd7b6585e39f86cbee29419de8768a8f97760066402bfb41a55ad1fce6f7ee98969d89499992bb16fd73fefca138441f6c3d88ff6c78b0a33b70453622ac9c5e99e6f45d87746457c6fb2624e9a4aa5b5b3e03a25d53eb3fd3cfbf1d06fb08f2ed67cf8ff84a16df064f7a1a3f8b05d406c7ac9afb1bc94abe155a79124c6d04120780226607ecee61a441a4e609e4a6fa8c63ab20ce4d908c1e9b561b0d5fec076a7715fed3d418ccddf30b80e21e5044c792e333a61d15176e882cad27b202676c97cf010d6056366f2810d6bf55593fc49746e495432c099e665fc21f5174d0dc0da98accf78d675fe6d3b1f4606f5a30e25a4b1afadd71457fee97a753f96b113ef04e988fb5df3ac8ad9e6023345768e1c13b34079ab98174ef4c4ffcce690ae04bbc062369d3b2ddd56b41780f17131130b5ab95a135d3bab9a6bccd17a34b5a28801ea403d3c9e0c9e0bdf36067e3b654701705207b797687b9a1095629e7eb19be29a9c97d7922d7419ca652bb1be87ff4d808a9fb30d3e0a110b62df6f25ccf37a54ee20787f3783b1830fea9b554c0ebbae8016dd914b6514a3ac6ed4fc519feda0f675c52a635f"


print(decrypt(decrytext, 'C91E3059132AABB599B7C992A572F48E'))
import requests
import config
# from Crypto import Random
from Crypto.Random import random
from Crypto.PublicKey import ElGamal
from Crypto.Util.number import GCD
import random
import numpy as np
# from app import Node as Node
# import json

def get_public_key(ip, port):
    URL='http://'+ip+':'+str(port)+'/public_key'
    r = requests.get(url=URL)
    data = r.json()
    return ElGamal.construct((int(data['p']), int(data['g']), int(data['y'])))
#
def encrypt(key, data):
    while 1:
        k = random.randint(1, key.p - 1)
        if GCD(k, key.p - 1) == 1: break
    encrypted = [key.encrypt(i, k) for i in data]
    return encrypted
#
#
# node1 = Node.Node('key1.txt')
# node2 = Node.Node('key2.txt')
# node3 = Node.Node('key3.txt')

#
# def multi_encrypt(data):
#     keys = [node1.key.y]
#     encrypt1 = node1._encrypt(data)
#     encrypt2 = node2.encrypt_cipher(encrypt1, keys)
#     keys.append(node2.key.y)
#     encrypt3 = node3.encrypt_cipher(encrypt2, keys)
#     return encrypt3
#
# def multi_decrypted(data):
#     decrypt1 = node1.decrypt_multi_cipher(data, [node2.key.y, node3.key.y])
#     decrypt2 = node2.decrypt_multi_cipher(decrypt1, [node3.key.y])
#     res = node3.decrypt(decrypt2)
#     return res
#
# cloud1 = [1, 0]
# cloud1_encrypted = multi_encrypt(cloud1)
# print(multi_decrypted(cloud1_encrypted))
# cloud2 = [1, 1]
# cloud2_encrypted = multi_encrypt(cloud2)
# pairs = [[cloud1_encrypted[0], cloud2_encrypted[0]], [cloud1_encrypted[1], cloud2_encrypted[1]]]

def multi_encrypt(cipher, ip, port):
    URL = 'http://' + ip + ':' + str(port) + '/encrypt'
    data = {'cipher': cipher,
            'encrypter_id': config.SERVER_A_HOSTNAME}
    # sending post request and saving response as response object
    r = requests.post(url=URL, json=data)
    return r.json()['cipher']

def get_overlap(pairs, ip, port):
    URL = 'http://' + ip + ':' + str(port) + '/overlap'
    data = {'crypto_list': pairs}
    # sending post request and saving response as response object
    r = requests.post(url=URL, json=data)
    return r.json()['overlap']

def verify(cloud, isp, ip, port):
    URL = 'http://' + ip + ':' + str(port) + '/verify'
    data = {'cloud': cloud, 'isp': isp}
    # sending post request and saving response as response object
    r = requests.post(url=URL, json=data)
    return r.json()['res']

num_isp = 3
cloud1 = [2, 1, 2]
key = get_public_key(config.SERVER_A_IP, config.PORT)
encrypted = encrypt(key, cloud1)
multi_encryption_1 = multi_encrypt(encrypted, config.SERVER_B_IP, config.PORT)
cloud2 = [2, 1, 2]
encrypted = encrypt(key, cloud2)
multi_encryption_2 = multi_encrypt(encrypted, config.SERVER_B_IP, config.PORT)
pairs=[]
for i in range(num_isp):
    pairs.append([multi_encryption_1[i], multi_encryption_2[i]])
res = get_overlap(pairs, config.SERVER_A_IP, config.PORT)
print(res)

# cloud = [2, 1, 1]
# key = get_public_key(config.SERVER_A_IP, config.PORT)
# encrypted = encrypt(key, cloud)
# cloud_encrypted = multi_encrypt(encrypted, config.SERVER_B_IP, config.PORT)
# isp = [2, 2, 1]
# encrypted = encrypt(key, isp)
# isp_encrypted = multi_encrypt(encrypted, config.SERVER_B_IP, config.PORT)
# res = verify(cloud_encrypted, isp_encrypted, config.SERVER_A_IP, config.PORT)
# print(res)

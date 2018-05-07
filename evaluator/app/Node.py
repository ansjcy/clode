from Crypto import Random
from Crypto.Random import random
from Crypto.PublicKey import ElGamal
from Crypto.Util.number import GCD
import random
import math
import config
import sys
import requests
from app.utils import inverse

class Node:
    def __init__(self, hostname):
        # with open('key.pkl', 'rb') as input:
        #     self.key = pickle.load(input)
        # self.key = ElGamal.generate(1024, Random.new().read)
        # with open('key.txt', 'w') as f:
        #     f.write(str(self.key.p) + '\n')
        #     f.write(str(self.key.g) + '\n')
        #     f.write(str(self.key.y) + '\n')
        #     f.write(str(self.key.x) + '\n')
        self.hostname = hostname
        if self.hostname == config.SERVER_A_HOSTNAME:
            path = 'key1.txt'
        elif self.hostname == config.SERVER_B_HOSTNAME:
            path = 'key2.txt'
        elif self.hostname == config.SERVER_C_HOSTNAME:
            path = 'key3.txt'
        else:
            print('invalid hostname')
            sys.exit(1)

        with open(path, 'r') as f:
            p = config.P
            g = config.G
            x = int(f.readline())
            y = int(f.readline())
        self.key = ElGamal.construct((p, g, y, x))
        print('finish initialization')

    def config(self):

        self.key_dict={}
        self.neighbors={}
        if self.hostname == config.SERVER_A_HOSTNAME:
            self.ip = config.SERVER_A_IP
            self.neighbors[config.SERVER_B_HOSTNAME] = config.SERVER_B_IP
            self.neighbors[config.SERVER_C_HOSTNAME] = config.SERVER_C_IP
            self.key_dict[config.SERVER_B_HOSTNAME] = config.SERVER_B_PUB_KEY
            self.key_dict[config.SERVER_C_HOSTNAME] = config.SERVER_C_PUB_KEY
        elif self.hostname == config.SERVER_B_HOSTNAME:
            self.ip = config.SERVER_B_IP
            self.neighbors[config.SERVER_A_HOSTNAME] = config.SERVER_A_IP
            self.neighbors[config.SERVER_C_HOSTNAME] = config.SERVER_C_IP
            self.key_dict[config.SERVER_A_HOSTNAME] = config.SERVER_A_PUB_KEY
            self.key_dict[config.SERVER_C_HOSTNAME] = config.SERVER_C_PUB_KEY
        elif self.hostname == config.SERVER_C_HOSTNAME:
            self.ip = config.SERVER_C_IP
            self.neighbors[config.SERVER_A_HOSTNAME] = config.SERVER_A_IP
            self.neighbors[config.SERVER_B_HOSTNAME] = config.SERVER_B_IP
            self.key_dict[config.SERVER_B_HOSTNAME] = config.SERVER_B_PUB_KEY
            self.key_dict[config.SERVER_A_HOSTNAME] = config.SERVER_A_PUB_KEY
        else:
            print('invalid hostname')
            sys.exit(1)
        self.next_port = config.PORT
        print('server %s starts...' % self.hostname)
        print('server ip: %s' % self.ip)

    def get_public_key(self):
        return {'p': int(self.key.p),
                'g': int(self.key.g),
                'y': int(self.key.y)}

    def decrypt(self, crypto_list):
        decrypted_list = []
        for crypto_pair in crypto_list:
            decrypted_pair = [self.key._decrypt(c) for c in crypto_pair]
            decrypted_list.append(decrypted_pair)
        random.shuffle(decrypted_list)
        return decrypted_list

    def _encrypt(self, data):
        p = int(self.key.p)
        while 1:
            k = random.randint(1, p - 1)
            if GCD(k, p - 1) == 1: break
        encrypted = [self.key.publickey().encrypt(i, k) for i in data]
        return encrypted

    def encrypt(self, cipher, encrypter_id):
        pub_keys = [self.key_dict[encrypter_id]]
        cipher = self.encrypt_cipher(cipher, pub_keys)
        pub_keys.append(int(self.key.y))
        for id in self.key_dict:
            if id != encrypter_id:
                cipher = self.get_encrypted_from_next(id, cipher, pub_keys)
                pub_keys.append(self.key_dict[id])
        return cipher

    def get_encrypted_from_next(self, id, cipher, pub_keys):
        ip = self.neighbors[id]
        URL = 'http://' + ip + ':' + str(config.PORT) + '/encrypt_cipher'
        data = {'cipher': cipher,
                'pub_keys': pub_keys}

        # sending post request and saving response as response object
        r = requests.post(url=URL, json=data)
        return r.json()['cipher']

    def encrypt_cipher(self, cipher, pub_keys):
        p = int(self.key.p)
        g = int(self.key.g)
        x = int(self.key.x)
        while 1:
            k = random.randint(1, p - 1)
            if GCD(k, p - 1) == 1: break
        encrypted = []
        for c in cipher:
            c1 = int(c[0])
            c2 = int(c[1])
            c1_ = (c1 * pow(g, k, p)) % p
            prod = 1
            for y in pub_keys:
                prod *= pow(int(y), k, p)
                prod %= p
            c2_ = (((c2 * prod) % p) * pow(c1_, x, p)) % p
            encrypted.append((c1_,c2_))
        return encrypted

    def _decrypt_cipher(self, crypto_list):
        keys = dict(self.key_dict)
        decrypted_list = self.decrypt_multi_cipher(crypto_list, list(keys.values()))
        for id in self.key_dict:
            keys.pop(id, None)
            if len(keys) != 0:
                print('get decrypt from %s' % id)
                decrypted_list = self.get_decrypted_from_next(id, decrypted_list, list(keys.values()))
            else:
                print('get plaintext from %s' % id)
                decrypted_list = self.get_plaintext_from_next(id, decrypted_list)
        print(decrypted_list)
        return decrypted_list

    def get_decrypted_from_next(self, id, cipher, pub_keys):
        ip = self.neighbors[id]
        URL = 'http://' + ip + ':' + str(config.PORT) + '/decode_multi_cipher'
        data = {'crypto_list': cipher,
                'pub_keys': pub_keys}

        # sending post request and saving response as response object
        r = requests.post(url=URL, json=data)
        return r.json()['decoded']

    def get_plaintext_from_next(self, id, cipher):
        ip = self.neighbors[id]
        URL = 'http://' + ip + ':' + str(config.PORT) + '/decode_cipher'
        data = {'crypto_list': cipher}

        # sending post request and saving response as response object
        r = requests.post(url=URL, json=data)
        return r.json()['plaintext']

    def decrypt_multi_cipher(self, crypto_list, pub_keys):
        p = int(self.key.p)
        g = int(self.key.g)
        x = int(self.key.x)
        while 1:
            k = random.randint(1, p - 1)
            if GCD(k, p - 1) == 1: break
        decrypted_list = []
        for cipher_pair in crypto_list:
            decrypted_pair = []
            for c in cipher_pair:
                c1 = int(c[0])
                c2 = int(c[1])
                c1_ = (c1 * pow(g, k, p)) % p
                prod = 1
                for y in pub_keys:
                    y = int(y)
                    prod *= pow(y, k, p)
                    prod %= p
                c1_pow = pow(c1, x, p)
                c2_ = (((c2 * prod) % p) * inverse(c1_pow, p)) % p
                decrypted_pair.append((c1_, c2_))
            decrypted_list.append(decrypted_pair)
            random.shuffle(decrypted_list)
        return decrypted_list

    def calculate(self, pairs):
        cnt = 0
        n = len(pairs[0])
        for p in pairs:
            if sum(p) == n * config.BASE:
                cnt += 1
        return float(cnt)/len(pairs)

    def get_overlap(self, crypto_list):
        plaintext_pairs = self._decrypt_cipher(crypto_list)
        return self.calculate(plaintext_pairs)


    def verify(self, cloud, isp):
        mul = []
        for i in range(len(cloud)):
            mul.append([self.cipher_div(cloud[i], isp[i])])
        res = self._decrypt_cipher(mul)
        for r in res:
            if r[0] != 1:
                return False
        return True


    def cipher_mul(self, a, b):
        return (a[0] * b[0], a[1] * b[1])

    def cipher_div(self, a, b):
        p = int(self.key.p)
        return ((a[0] * inverse(b[0], p)) % p, (a[1] * inverse(b[1], p) % p))

    def test_encrypt_multi(self):
        c=2
        a=c**1
        b=c**1
        encrypt_a = self.encrypt([a])[0]
        encrypt_b = self.encrypt([b])[0]
        cipher_mul = (encrypt_a[0] * encrypt_b[0] , encrypt_a[1] * encrypt_b[1])
        decrypted = self.key.decrypt(cipher_mul)
        print('add result: %d' % math.log(decrypted, c))



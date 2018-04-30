import http.client
import json
from Crypto import Random
from Crypto.Random import random
from Crypto.PublicKey import ElGamal
from Crypto.Util.number import GCD
import random
import pickle
import math
import config
import sys
import socket

class Node:
    def __init__(self):
        # with open('key.pkl', 'wb') as output:
        #     self.key = ElGamal.generate(1024, Random.new().read)
        #     pickle.dump(self.key, output, pickle.HIGHEST_PROTOCOL)
        # with open('key.pkl', 'rb') as input:
        #     self.key = pickle.load(input)
        # self.key = ElGamal.generate(1024, Random.new().read)
        # with open('key.txt', 'w') as f:
        #     f.write(str(self.key.p) + '\n')
        #     f.write(str(self.key.g) + '\n')
        #     f.write(str(self.key.y) + '\n')
        #     f.write(str(self.key.x) + '\n')
        with open('key.txt', 'r') as f:
            p = f.readline()
            g = f.readline()
            y = f.readline()
            x = f.readline()
            self.key = ElGamal.construct((int(p), int(g), int(y), int(x)))
        print('finish initialization')

    def config(self):
        self.hostname = socket.gethostname()
        if self.hostname == config.SERVER_A_HOSTNAME:
            self.ip = config.SERVER_A_IP
            self.next_ip = config.SERVER_B_IP
        elif self.hostname == config.SERVER_B_HOSTNAME:
            self.ip = config.SERVER_B_IP
            self.next_ip = config.SERVER_C_IP
        elif self.hostname == config.SERVER_C_HOSTNAME:
            self.ip = config.SERVER_C_IP
            self.next_ip = config.SERVER_A_IP
        else:
            print('invalid hostname')
            sys.exit(1)
        self.next_port = config.PORT
        print('server %s starts...' % self.hostname)
        print('server ip: %s' % self.ip)

    def get_public_key(self):
        return {'p': str(self.key.p),
                'g': str(self.key.g),
                'y': str(self.key.y)}

    def decrypt(self, crypto_list):
        decrypted = [[self.key.decrypt(cipher) for cipher in pair] for pair in crypto_list]
        return decrypted


    def shuffle(self, crypto_list):
        return random.shuffle(crypto_list)

    def get_decrypt_from_next(self, crypto_list, remain_shuf_times):
        conn = http.client.HTTPConnection(self.next_ip, self.next_port)
        params = json.dumps({'crpto_list': crypto_list, 'remain_shuf_times': remain_shuf_times})
        headers = {"Content-type": "application/json"}
        conn.request("POST", "/query", params, headers)
        res = conn.getresponse()
        print(res.status, res.reason)
        data = res.read().get_json()
        conn.close()
        return data['overlap']

    def encrypt(self, data):
        while 1:
            k = random.randint(1, self.key.p - 1)
            if GCD(k, self.key.p - 1) == 1: break
        encrypted = [self.key.publickey().encrypt(i, k) for i in data]
        return encrypted

    def calculate(self, pairs):
        print("test")
        cnt = 0
        n = len(pairs[0])
        for p in pairs:
            if sum(p) == n:
                cnt += 1
        return float(cnt)/len(pairs)

    def get_overlap(self, crypto_list, remain_shuf_times):
        decoded = self.decrypt(crypto_list)
        shuffled = self.shuffle(decoded)
        if remain_shuf_times == 1:
            return self.calculate(shuffled)
        else:
            return self.get_decrypt_from_next(shuffled, remain_shuf_times-1)

    def test_encrypt_multi(self):
        c=2
        a=c**1
        b=c**1
        encrypt_a = self.encrypt([a])[0]
        encrypt_b = self.encrypt([b])[0]
        cipher_mul = (encrypt_a[0] * encrypt_b[0], encrypt_a[1] * encrypt_b[1])
        decrypted = self.key.decrypt(cipher_mul)
        print('add result: %d' % math.log(decrypted, c))



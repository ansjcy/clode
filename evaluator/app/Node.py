import http.client
import json
from Crypto import Random
from Crypto.Random import random
from Crypto.PublicKey import ElGamal
from Crypto.Util.number import GCD
import random
import pickle
import math

class Node:
    def __init__(self, ip):
        print("init node")
        self.ip = ip
        # with open('key.pkl', 'wb') as output:
        #     self.key = ElGamal.generate(1024, Random.new().read)
        #     pickle.dump(self.key, output, pickle.HIGHEST_PROTOCOL)
        with open('key.pkl', 'rb') as input:
            self.key = pickle.load(input)
        print(ip)

    def set_port(self, port):
        self.port = port

    def set_next(self, nip, nport):
        self.nip = nip
        self.nport = nport

    def get_public_key(self):
        return pickle.dumps(self.key.publickey())

    def decrypt(self, crypto_list):
        decrypted = [[self.key.decrypt(cipher) for cipher in pair] for pair in crypto_list]
        return decrypted


    def shuffle(self, crypto_list):
        return random.shuffle(crypto_list)

    def get_decrypt_from_next(self, crypto_list, remain_shuf_times):
        conn = http.client.HTTPConnection(self.nip, self.nport)
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



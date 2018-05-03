import requests
import config
import time
import pickle
import random
import math
from Crypto.PublicKey import ElGamal
from Crypto.Util.number import GCD

transactions = []
cloud_name = ""
pkeys = []
isps = []

def view():

    quit = False
    while (not quit):

        choose = int(input("choose:\n   \
        1. add new transaction    2. show transaction record    3.quit:\n"))

        if choose == 1:

            trans_id = input("please input transaction id:\n")
            ISP_name = input("please input ISP name:\n")
            transactions.append([trans_id, ISP_name, 1])

            data_list = []
            for isp in isps:
                data = {
                    'cloud_id': cloud_name,
                    'transaction_id': trans_id,
                    'isp_id': isp,
                    'data': encrypt(0)
                }
                if isp == ISP_name:
                    data['data'] = encrypt(1)
                data_list.append(data)

            requests.post(url='http://' + config.blockchain_address + config.port + '/crypto',
                                   json={'transactions': data_list})
            print ("transaction already sent to blockchain!")

        elif choose == 2:

            print ("transaction id | cloud name")
            for trans in transactions:
                print ('%14s   %10s' %(trans[0], trans[1]))
            print ("")

        elif choose == 3:

            print ("goodbye!")
            quit = True

        else:

            print ("invalid choice")

def allocate_key(address_list):

    for address in address_list:
        res = requests.get(url=address + config.port + '/public_key')
        res = res.json()
        p = res['p']
        g = res['g']
        y = res['y']
        pkey = ElGamal.construct((int(p), int(g), int(y)))
        pkeys.append(pkey)

    return pkeys


def encrypt(data):
    data = int(math.pow(2, data))

    for pkey in pkeys:
        while 1:
            k = random.randint(1, pkey.p - 1)
            if GCD(k, pkey.p - 1) == 1: break
        data = pkey.publickey().encrypt(data, k)

    res = requests.post(config.encrypt_address + config.port + '/encrypt',
                  json = {'encrypter_id': 'ip-172-31-16-11',
                          'cipher': data})


    return res.json()


if __name__ == '__main__':
    cloud_name = input("please set cloud name:\n")

    allocate_key(config.CA_address)
    print ("key allocation succceed!")

    res = requests.get("http://" + config.blockchain_address + config.port + '/get_isp')
    isps = res.json()
    print ("get isps successfully!")

    view()




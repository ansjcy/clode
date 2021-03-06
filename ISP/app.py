from flask import Flask, jsonify, request
from multiprocessing import Process
import socket
import requests
import config
import time
import pickle
import random
import math
from Crypto.PublicKey import ElGamal
from Crypto.Util.number import GCD

transactions = []
server_name = ""
pkeys = []

def allocate_key(address_list):

    for address in address_list:
        res = requests.get(url="http://" + address + config.port + '/public_key')
        res = res.json()
        p = res['p']
        g = res['g']
        y = res['y']
        pkey = ElGamal.construct((int(p), int(g), int(y)))
        pkeys.append(pkey)

    return pkeys

allocate_key(config.CA_address)
print ("key allocation succceed!")
print(pkeys)

def view():

    print ('loading...')
    time.sleep(2)

    quit = False
    while (not quit):

        choose = int(input("choose:\n   1. add new transaction    2. show transaction record    3.quit:\n"))

        if choose == 1:

            trans_id = input("please input transaction id:\n")
            cloud_name = input("please input cloud name:\n")
            transactions.append([trans_id, cloud_name, 1])
            with open('./data/transactions', 'wb') as tf:
                pickle.dump(transactions, tf)

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



def encrypt(data):
    data = int(math.pow(2, data))
    print(pkeys)
    for pkey in pkeys:
        while 1:
            k = random.randint(1, pkey.p - 1)
            if GCD(k, int(pkey.p - 1)) == 1: break
        data = [pkey.publickey()._encrypt(data, k)]
    print('fuck')
    print(data)

    res = requests.post(url = "http://" + config.encrypt_server + config.port + '/encrypt',
                  json = {'encrypter_id': 'ip-172-31-16-11',
                          'cipher': data})


    return res.json()


if __name__ == '__main__':
    print ("please set server name!")
    server_name = input("")


    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    print (myaddr)
    res = requests.post(url="http://" + config.blockchain_address + config.port + '/register_isp', json={'address': myaddr, 'name': server_name})
    print ("ISP register succeed!")

    import controller.index as index

    p = Process(target=index.app.run, args=(myaddr, index.port))
    p.start()
    print ("server running!")

    view()
    p.terminate()
    p.join()




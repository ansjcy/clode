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
        res = requests.get(url="http://" + address + config.port + '/public_key')
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

    res = requests.post(url = "http://" + config.encrypt_address + config.port + '/encrypt',
                  json = {'encrypter_id': 'ip-172-31-16-11',
                          'cipher': data})


    return res.json()


if __name__ == '__main__':
    print ("please set server name!")
    server_name = input("")

    allocate_key(config.CA_address)
    print ("key allocation succceed!")

    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    res = requests.post(url="http://" + config.blockchain_address + config.port + '/register_ISP', json={'address': myaddr, 'name': myname})
    print ("ISP register succeed!")

    import controller.index as index

    p = Process(target=index.app.run, args=(config.host, index.port))
    p.start()
    print ("server running!")

    view()
    p.terminate()
    p.join()




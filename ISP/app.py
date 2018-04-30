from flask import Flask, jsonify, request
from multiprocessing import Process
import socket
import requests
import config
import time
import pickle

transactions = []
server_name = ""
loading = True
pkeys = []

def view():

    while loading:
        time.sleep(0.1)

    quit = False
    while (not quit):

        print ("choose: 1. add new transaction    2. show transaction record    3.quit")
        choose = input()

        if choose == 1:

            print ("please input transaction id, cloud name")
            trans_id = input()
            cloud_name = input()
            transactions.append([trans_id, cloud_name])

        elif choose == 2:

            print ("transaction id | cloud name")
            for trans in transactions:
                print ('%16s   %s' %(trans[0], trans[1]))

        elif choose == 3:

            print ("goodbye!")
            quit = True

        else:

            print ("invalid choice")

def allocate_key(address_list):
    return

    for address in address_list:
        res = requests.get(url=address + '/public_key')
        res = res.json()
        pkeys.append(pickle.loads(res['public_key']))

    return pkeys


def encrypt(data):

    for pkey in pkeys:
        pass
    return 0


if __name__ == '__main__':
    print ("please set server name!")
    server_name = input("")

    allocate_key(config.CA_address)
    print ("key allocation succceed!")

    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    ##res = requests.post(url=config.blockchain_address + '/register_ISP', data={'address': myaddr, 'name': myname})
    print ("ISP register succeed!")

    p = Process(target=view)
    p.start()

    import controller.app
    loading = False




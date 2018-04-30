from flask import Flask, jsonify, request
from multiprocessing import Process
import socket
import requests
import config
import time
import pickle

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
    res = requests.post(url=config.blockchain_address + port + '/register_ISP', json={'address': myaddr, 'name': myname})
    print ("ISP register succeed!")

    import controller.index as index

    p = Process(target=index.app.run, args=(config.host, index.port))
    p.start()
    print ("server running!")

    view()
    p.terminate()
    p.join()




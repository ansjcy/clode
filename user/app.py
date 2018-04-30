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

def view():

    quit = False
    while not quit:

        choose = int(input("please enter choice:\n"
                       "1. query    2. quit\n"))

        if choose == 1:

            n = int(input("please enter cloud amount!\n"))
            cloud_list = []
            for i in range(n):
                print("please enter cloud name")
                cloud_list.append(input())

            res = requests.get(url=config.blockchain_address + config.port + '/query', json={'cloud_list': cloud_list})
            res = res.json()
            print("overlap: %d" % res)

        elif choose == 2:

            quit = True

        else:

            print("invalid choice!")

if __name__ == '__main__':
    view()



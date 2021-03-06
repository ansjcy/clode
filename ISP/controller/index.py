import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from app import transactions, encrypt, pkeys
from flask import Flask, jsonify, request
from uuid import uuid4
import socket
import requests
import pickle

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

@app.route('/get_transaction', methods=['POST'])
def get_transaction():

    values = request.get_json()
    required = ['transaction_id', 'cloud_id']
    if not all(k in values for k in required):
        return 'Missing values', 400

    transaction_id = values.get('transaction_id')
    cloud_id = values.get('cloud_id')

    with open('./data/transactions', 'rb') as tf:
        transactions = pickle.load(tf)

    for transaction in transactions[::-1]:

        print(transaction[0])
        print(transaction_id)
        if transaction[0] == transaction_id:

            print('OK')

            if cloud_id == transaction[1]:
                response = {
                    'data': encrypt(transaction[2])
                }
                return jsonify(response), 201

            else:
                response = {
                    'data': encrypt(2)
                }
                return jsonify(response), 201

    response = {
        'data': encrypt(0)
    }
    return jsonify(response), 201


from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
args = parser.parse_args()
port = args.port
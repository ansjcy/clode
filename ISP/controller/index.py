import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from app import transactions, encrypt, pkeys
from flask import Flask, jsonify, request
from uuid import uuid4
import socket
import requests

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

@app.route('/get_transaction', methods=['POST'])
def get_transaction():

    values = request.get_json()
    required = ['transaction_id']
    if not all(k in values for k in required):
        return 'Missing values', 400

    transaction_id = values.get('transaction_id')
    for transaction in transactions[::-1]:
        if transaction[0] == transaction_id:
            response = {
                'cloud_id': transaction[1],
                'data': encrypt(transaction[2])
            }
            return jsonify(response), 201

    return 400


from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
args = parser.parse_args()
port = args.port

app.run(host='0.0.0.0', port=port)
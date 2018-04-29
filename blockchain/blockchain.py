import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request
import config
import socket
from promise import Promise


class Blockchain:
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.isps = {} # key: isp name, value: isp address.

        self.new_block(previous_hash='1', proof=100)


    def new_block(self, proof, previous_hash):

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': [],
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.chain.append(block)
        return block

    def new_transaction(self, cloud_id, isp_id, data):

        self.chain[-1]['transactions'].append({
            'cloud_id': cloud_id,
            'isp_id': isp_id,
            'data': data,
        })
        return


    def register_node(self, address):

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    @staticmethod
    def hash(block):

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

buffer = {
    # transaction_id : [{}]
}



@app.route('/crypto', methods=['POST'])
def post_crypto():

    # def fun(resolve, reject, address):
    #     requests.post(url=neighbor + '/get_transaction', data={'transaction_id': values.get('transaction_id')})
    #     resolve('')
    def equal(data1, data2):
        return data1 - data2 == 0

    values = request.get_json()
    required = ['cloud_id', 'transaction_id', 'isp_id', 'data']
    if not all(k in values for k in required):
        return 'Missing values', 400
    transaction_id = values.get('transaction_id')
    cloud_id = values.get('cloud_id')
    isp_id = values.get('isp_id')
    data = values.get('data')
    buffer[transaction_id] = []
    for isp in blockchain.isps:
        result = requests.post(url=blockchain.isps[isp] + '/get_transaction', data={'transaction_id': transaction_id}).json()
        buffer[transaction_id].append({
            'cloud_id': cloud_id,
            'isp_id': result['isp_id'],
            'data': result['data']
        })
    # ready to do evaluation.
    sum = 0
    for trans in buffer[transaction_id]:
        sum += trans.data
    if not equal(sum, data):
        return 'Wrong value provided!', 400
    blockchain.new_transaction(cloud_id, isp_id, data)
    return 'post transaction success!', 201


@app.route('/register_node', methods=['POST'])
def register_node():
    values = request.get_json()
    required = ['address']
    if not all(k in values for k in required):
        return 'Missing values', 400
    address = values.get('address')
    if address not in blockchain.nodes:
        blockchain.register_node(address)
        for neighbor in blockchain.nodes:
            requests.post(url=neighbor+'/register_node', data={'address': address})

    response = {
        'address_list': list(blockchain.nodes)
    }
    return jsonify(response), 201


@app.route('/register_isp', methods=['POST'])
def register_isp():
    values = request.get_json()
    required = ['address', 'name']
    if not all(k in values for k in required):
        return 'Missing values', 400
    address = values.get('address')
    name = values.get('name')
    blockchain.isps[name] = address
    return 'register isp success!', 201


@app.route('/query', methods=['POST'])
def query():
    values = request.get_json()
    required = ['cloud_list']
    if not all(k in values for k in required):
        return 'Missing values', 400
    cloud_list = values.get('cloud_list')
    if len(cloud_list) < 2:
        return 'cloud list too short!', 400
    cloud_trans = {}
    for id in cloud_list:
        cloud_trans[id] = {}
    for block in blockchain.chain:
        for trans in block['transactions']:
            for id in cloud_list:
                if trans['cloud_id'] == id:
                    if trans['isp_id'] not in cloud_trans[id]:
                        cloud_trans[id][trans['isp_id']] = 0
                    cloud_trans[id][trans['isp_id']]+=1
    query_body = []

    requests.post(url=config.evaluator_address + '/query', data={'crypto_list': query_body})
    return

@app.route('/get_chain', methods=['GET'])
def get_chain():
    return jsonify({'chain': blockchain.chain}), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
    myname = socket.getfqdn(socket.gethostbyname())
    myaddr = socket.gethostbyname(myname)
    print(myname)
    print(myaddr)
    if myaddr != config.blockchain_address:
        requests.post(url=config.blockchain_address+'/register_node', data={'address': myaddr})

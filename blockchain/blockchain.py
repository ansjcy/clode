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
        self.isps = {}
        self.isp_num = 0

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

    def register_isp(self, isp_name, isp_address):
        if isp_name not in self.isps:
            self.isps[isp_name] = (self.isp_num, isp_address)
            self.isp_num += 1

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """

        previous_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{previous_block}')
            print(f'{block}')
            print("\n-----------\n")

            previous_block_hash = self.hash(previous_block)
            if block['previous_hash'] != previous_block_hash:
                return False

            if not self.valid_proof(previous_block['proof'], block['proof'], previous_block_hash):
                return False

            previous_block = block
            current_index += 1

        return True

    def __getitem__(self, idx):
        return self.chain[idx]

    def resolve_conflicts(self):
        """
        consensus algorithm
        choose one with longest block
        """

        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(neighbours[node][1] + "/get_chain")

            if response.status_code == 200:
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if len(chain) > max_length and self.valid_chain(chain):
                    max_length = len(chain)
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof

        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @property
    def last_block(self):
        return self.chain[-1]

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

    values = request.get_json()
    required = ['type', 'cloud_id', 'transaction_id', 'isp_id', 'data']
    if not all(k in values for k in required):
        return 'Missing values', 400
    transaction_id = values.get('transaction_id')
    buffer[transaction_id] = []
    for neighbor in blockchain.nodes:
        result = requests.post(url=neighbor + '/get_transaction', data={'transaction_id': transaction_id})
        buffer[transaction_id].append({
            cloud_id:
        })

        # ready to do evaluation.

@app.route('/register_node', methods=['POST'])
def post_crypto():
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
    return

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

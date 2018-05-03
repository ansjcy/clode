import hashlib
import json
import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask, jsonify, request
import config
import socket
from multiprocessing import Process
import pickle
import random
import math
from Crypto.PublicKey import ElGamal
from Crypto.Util.number import GCD

myname = socket.getfqdn(socket.gethostname())
myaddr = socket.gethostbyname(myname)
pkeys = []

class Blockchain:
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.isps = {} # key: isp name, value: isp address.
        self.current_trans = []

        self.new_block(previous_hash='1', proof=100)


    def new_block(self, proof, previous_hash):

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': [],
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        block['transaction'] = self.current_trans
        self.current_trans = []
        self.chain.append(block)
        return block

    def new_transaction(self, cloud_id, isp_id, data):

        self.current_trans.append({
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

    @staticmethod
    def mine(blockchain):

        while (not exit_signal):
            start_time = time.time()

            proof = blockchain.proof_of_work(blockchain.last_block)
            prev_hash = blockchain.hash(blockchain.last_block)

            with open(config.transactions_file, 'rb') as tf:
                current_trans = pickle.load(tf)
                blockchain.current_trans = current_trans
                blockchain.new_block(proof, prev_hash)
                with open(config.chain_file, 'wb') as cf:
                    pickle.dump(blockchain.chain, cf)

            with open(config.transactions_file, 'wb') as tf:
                pickle.dump([], tf)

            end_time = time.time()

            if end_time - start_time < config.mine_time:
                time.sleep(max(0, config.mine_time - (end_time - start_time)))
            print ('a new mine, current number of blocks: %d' %len(blockchain.chain))

    @property
    def last_block(self):
        return self.chain[-1]

# buffer = {
#     # transaction_id : encrypted value #[{}]
# }

# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# signal exit to mine
exit_signal = False

def allocate_key(address_list):

    for address in address_list:
        res = requests.get(url='http://' + address + config.port + '/public_key')
        res = res.json()
        p = res['p']
        g = res['g']
        y = res['y']
        pkey = ElGamal.construct((int(p), int(g), int(y)))
        pkeys.append(pkey)

    return pkeys



@app.route('/crypto', methods=['POST'])
def post_crypto():

    # give company list and isp list
    def equal(data1, data2):
        print(data1)
        print(data2)
        result = requests.post(url='http://' + config.CA_addresses[0] + config.port + '/verify', json={'cloud': data1, 'isp': data2}).json()
        print(result)
        return result['res']
    values = request.get_json()
    # required = ['cloud_id', 'transaction_id', 'isp_id', 'data']
    # if not all(k in values for k in required):
    #     return 'Missing values', 400
    # transaction_id = values.get('transaction_id')
    # cloud_id = values.get('cloud_id')
    # isp_id = values.get('isp_id')
    # data = values.get('data')
    required = ['transactions']
    if not all(k in values for k in required):
        return 'Missing values', 400
    transactions = values.get('transactions')

    # buffer[transaction_id] = []
    # for isp in blockchain.isps:
    #     result = requests.post(url=blockchain.isps[isp] + '/get_transaction', json={'transaction_id': transaction_id}).json()
    #     buffer[transaction_id].append({
    #         'cloud_id': cloud_id,
    #         'isp_id': result['isp_id'],
    #         'data': result['data']
    #     })

    # result = requests.post(url='http://' + blockchain.isps[isp_id] + config.port + '/get_transaction',
    #                        json={'transaction_id': transaction_id}).json()
    # if not equal(result['data'], data) or not cloud_id == result['cloud_id']:
    #     return 'Wrong value!', 400
    company_list = []
    isp_list = []
    for d in transactions:
        transaction_id = d['transaction_id']
        cloud_id = d['cloud_id']
        isp_id = d['isp_id']
        data = d['data']
        result = requests.post(url='http://'+blockchain.isps[isp_id] + config.port + '/get_transaction', json={'transaction_id': transaction_id, 'cloud_id': cloud_id})
        result = result.json()
        company_list.append(data[0])
        isp_list.append(result['data']['cipher'][0])
    if not equal(company_list, isp_list):
        print('wrong value!')
        return 'Wrong value!', 400

    # transaction = [[cloud_id, isp, data] if isp == isp_id else [cloud_id, isp, encrypt(0)] for isp in blockchain.isps]
    # for each_tran in transaction:
    #     blockchain.new_transaction(*each_tran)
    with open(config.chain_file, 'rb') as cf:
        blockchain.chain = pickle.load(cf)
    for transaction in transactions:
        blockchain.new_transaction(transaction['cloud_id'], transaction['isp_id'], transaction['data'])
    with open(config.transactions_file, 'wb') as tf:
        pickle.dump(blockchain.current_trans, tf)

    for neighbor in blockchain.nodes:
        requests.post(url='http://'+ neighbor + config.port +'/new_transaction', json={'data': transactions})

    return 'post transaction success!', 201

@app.route('/new_transaction', methods=['POST'])
def new_trans():
    values = request.get_json()
    required = ['data']
    if not all(k in values for k in required):
        return 'Missing values', 400

    transactions = values.get('data')
    with open(config.chain_file, 'rb') as cf:
        blockchain.chain = pickle.load(cf)
    for transaction in transactions:
        blockchain.new_transaction(transaction['cloud_id'], transaction['isp_id'], transaction['data'])
    with open(config.transactions_file, 'wb') as tf:
        pickle.dump(blockchain.current_trans, tf)
    print (len(blockchain.chain))

    return 'broadcast transaction success!', 201


@app.route('/register_node', methods=['POST'])
def register_node():
    print("register_node")
    values = request.get_json()
    required = ['address']
    if not all(k in values for k in required):
        return 'Missing values', 400
    address = values.get('address')
    print(blockchain.nodes)
    print(address)
    if address not in blockchain.nodes and not address == myaddr:
        blockchain.register_node(address)
        for neighbor in blockchain.nodes:
            if neighbor == address:
                continue
            print("cascade register")
            requests.post(url='http://'+neighbor+config.port+'/register_node', json={'address': address})

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
    print('351' + str(address))
    print('352' + str(name))
    if name not in blockchain.isps:
        blockchain.isps[name] = address
        for neighbor in blockchain.nodes:
            requests.post(url='http://'+neighbor + config.port + '/register_isp', json=values)
    return 'register isp success!', 201


@app.route('/query', methods=['POST'])
def query():
    values = request.get_json()
    required = ['cloud_list']
    if not all(k in values for k in required):
        print('Missing values')
        return 'Missing values', 400
    cloud_list = values.get('cloud_list')
    if len(cloud_list) < 2:
        print('cloud list too short!')
        return 'cloud list too short!', 400
    cloud_trans = {}
    for id in cloud_list:
        cloud_trans[id] = {}
    for block in blockchain.chain:
        for trans in block['transactions']:
            for id in cloud_list:
                if trans['cloud_id'] == id:
                    if trans['isp_id'] not in cloud_trans[id]:
                        cloud_trans[id][trans['isp_id']] = [1, 1]
                    cloud_trans[id][trans['isp_id']][0] *= trans['data'][0]
                    cloud_trans[id][trans['isp_id']][1] *= trans['data'][1]
    for trans in blockchain.current_trans:
        for id in cloud_list:
            if trans['cloud_id'] == id:
                if trans['isp_id'] not in cloud_trans[id]:
                    cloud_trans[id][trans['isp_id']] = [1, 1]
                print(cloud_trans[id][trans['isp_id']])
                print(trans['data'])
                cloud_trans[id][trans['isp_id']][0] += trans['data'][0]
                cloud_trans[id][trans['isp_id']][1] += trans['data'][1]
    print(cloud_trans)
    query_body = []
    isps = cloud_trans[0].keys()
    for isp in isps:
        query_body.append([])
        for id in cloud_trans:
            query_body[-1].append(cloud_trans[id][isp])
    print(query_body)
    result = requests.post(url='http://'+config.CA_addresses[0] + config.port + '/overlap', json={'crypto_list': query_body}).json()
    return jsonify({'overlap': result['overlap']}), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    print(len(blockchain.chain))
    return jsonify({'chain': len(blockchain.chain)}), 200

@app.route('/get_isp', methods=['GET'])
def get_isp():
    return jsonify({'isp_list': blockchain.isps}), 200


if __name__ == '__main__':

    with open(config.transactions_file, 'wb') as tf:
        pickle.dump([], tf);

    p = Process(target=Blockchain.mine, args=(blockchain, ))
    p.start()

    print(myname)
    print(myaddr)
    if myaddr != config.blockchain_address:
        res = requests.post(url='http://'+config.blockchain_address + config.port +'/register_node', json={'address': myaddr})
        res_json = res.json()
        blockchain.nodes = set(res_json['address_list'])
        print("register node succeed!")

    allocate_key(config.CA_addresses)
    print("get public keys success!")

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host=myaddr, port=port)

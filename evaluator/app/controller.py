from app import app
from app import node
from flask import request
import json
import config

@app.route('/overlap', methods=['POST'])
def get_overlap():
    values = request.get_json()
    required = ['crypto_list']
    if not all(k in values for k in required):
        return 'Missing values', 400
    crypto_list = values['crypto_list']
    overlap = node.get_overlap(crypto_list)
    query_result = {'overlap': overlap}
    return json.dumps(query_result)

@app.route('/public_key', methods=['GET'])
def return_public_key():
    return json.dumps(node.get_public_key())

@app.route('/verify', methods=['POST'])
def verify():
    values = request.get_json()
    res = node.verify(values['cloud'], values['isp'])
    return json.dumps({'res': res})

@app.route('/encrypt', methods=['POST'])
def encrypt():
    values = request.get_json()
    cipher = node.encrypt(values['cipher'], values['encrypter_id'])
    return json.dumps({'cipher': cipher})

@app.route('/encrypt_cipher', methods=['POST'])
def encrypt_cipher():
    values = request.get_json()
    cipher = node.encrypt_cipher(values['cipher'], values['pub_keys'])
    return json.dumps({'cipher': cipher})

@app.route('/decode_multi_cipher', methods=['POST'])
def decode_multi_cipher():
    values = request.get_json()
    decoded = node.decrypt_multi_cipher(values['crypto_list'], values['pub_keys'])
    return json.dumps({'decoded': decoded})

@app.route('/decode_cipher', methods=['POST'])
def decode_cipher():
    values = request.get_json()
    plaintext = node.decrypt(values['crypto_list'])
    return json.dumps({'plaintext': plaintext})

@app.route('/echo', methods=['POST'])
def echo():
    print("receive request")
    values = request.get_json()
    resp = {"echo": values['text']}
    return json.dumps(resp)
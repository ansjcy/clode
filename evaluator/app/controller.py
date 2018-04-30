from app import app
from app import node
from flask import request
import json
import config

@app.route('/query', methods=['POST'])
def query():
    values = request.get_json()
    required = ['crypto_list']
    if not all(k in values for k in required):
        return 'Missing values', 400
    crypto_list = values['crypto_list']
    remain_shuf_times = config.NUM_NODES
    if values['remain_shuf_times'] != None:
        remain_shuf_times = values['remain_shuf_times']
    overlap = node.get_overlap(crypto_list, remain_shuf_times)
    query_result = {'overlap': overlap}
    return json.dumps(query_result)
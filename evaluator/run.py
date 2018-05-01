from app import app
from app import node
from argparse import ArgumentParser
import config
import socket

if __name__ == '__main__':

    # parser = ArgumentParser()
    # parser.add_argument('-i', '--server_id', type=str, help='node id')
    # args = parser.parse_args()
    app.run(host='0.0.0.0', port=config.PORT)


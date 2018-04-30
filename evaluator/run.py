from app import app
from app import node
from argparse import ArgumentParser

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-i', '--next_ip', type=str, help='ip of next node')
    parser.add_argument('-o','--next_port', default=5000, type=int, help='port of next node')

    args = parser.parse_args()
    port = args.port
    node.set_port(port)
    node.set_next(args.next_ip, args.next_port)
    app.run(host='0.0.0.0', port=port)


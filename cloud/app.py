import requests
import config
import time
import pickle

transactions = []
cloud_name = ""
pkeys = []

def view():

    quit = False
    while (not quit):

        choose = int(input("choose:\n   \
        1. add new transaction    2. show transaction record    3.quit:\n"))

        if choose == 1:

            trans_id = input("please input transaction id:\n")
            ISP_name = input("please input ISP name:\n")
            transactions.append([trans_id, ISP_name, 1])
            ['cloud_id', 'transaction_id', 'isp_id', 'data']
            data = {
                    'cloud_id': cloud_name,
                    'transaction_id': trans_id,
                    'isp_id': ISP_name,
                    'data': encrypt(1)
            }
            requests.post(url='http://' + config.blockchain_address + config.port + '/crypto',
                                   json=data)
            print ("transaction already sent to blockchain!")

        elif choose == 2:

            print ("transaction id | cloud name")
            for trans in transactions:
                print ('%14s   %10s' %(trans[0], trans[1]))
            print ("")

        elif choose == 3:

            print ("goodbye!")
            quit = True

        else:

            print ("invalid choice")

def allocate_key(address_list):

    for address in address_list:
        res = requests.get(url=address + config.port + '/public_key')
        res = res.json()
        pkeys.append(pickle.loads(res['public_key']))

    return pkeys


def encrypt(data):

    for pkey in pkeys:
        pass
    return 0


if __name__ == '__main__':
    cloud_name = input("please set cloud name:\n")

    allocate_key(config.CA_address)
    print ("key allocation succceed!")

    view()




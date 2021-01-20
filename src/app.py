import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


# creating a Black

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()
        # self.accounts = {'dillu':'dks', 'admin': 'pass'}
        self.accounts = {'0x28E98D1593f604e8E35EDBeb123160b90055baC3':{'public_key': '0x28E98D1593f604e8E35EDBeb123160b90055baC3',
                                                                       'private_key': 'bc0771a448c062a1a86ad128b124473f5121c895dd8a56a1c0a2f429785b88ec',
                                                                       'account_number': '0x28E98D1593f604e8E35EDBeb123160b90055baC3',
                                                                       'amount': 100},
                         '0xF5EcA7D099f91a1709724Fd6d60dbb4f2A5fC446':{'public_key': '0xF5EcA7D099f91a1709724Fd6d60dbb4f2A5fC446',
                                                                       'private_key': '5dbb8ac646a960514b6979362c2401e7c6189c7e667215b7b6153ca127256c57',
                                                                       'account_number': '0xF5EcA7D099f91a1709724Fd6d60dbb4f2A5fC446',
                                                                       'amount': 100},
                         '0x60355c86285aeA67DE32E218E2e1307e0ef87699': {'public_key': '0x60355c86285aeA67DE32E218E2e1307e0ef87699',
                                                                        'private_key':'84d3e8c6704ec19fd752f9c3ec3c8cfd4b4c09d20d45f2bf5221bd559ec3baa1',
                                                                        'account_number': '0x60355c86285aeA67DE32E218E2e1307e0ef87699',
                                                                        'amount': 100},
                         '0xc5A7911E96a9fB5ee855433a66d7A7E97d5D2A81': {'public_key': '0xc5A7911E96a9fB5ee855433a66d7A7E97d5D2A81',
                                                                        'private_key':'7af19af77273e6ecfce13516ce82d471dec069c51a7834d363413dea1fb1d16d',
                                                                        'acccont_number': '0xc5A7911E96a9fB5ee855433a66d7A7E97d5D2A81',
                                                                        'amount': 100},
                         '0xB1EF390d6fC4ae797a4e9ee21f4dA778a0524690': {'public_key': '0xB1EF390d6fC4ae797a4e9ee21f4dA778a0524690',
                                                                        'private_key':'31647ee912ae9158b3a24737178f718df9fc35be9673c39f2948a9a1ac975018',
                                                                        'acccont_number': '0xB1EF390d6fC4ae797a4e9ee21f4dA778a0524690',
                                                                        'amount': 100},

                         }

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions
                 }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        while 1:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                return new_proof
            else:
                new_proof += 1

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys = True).encode()).hexdigest()


    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            previous_block = block
            block_index += 1

        return True

    #crypto psrt
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    def replace_chain(self):
        network = self.nodes
        print(network)
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get('http://'+node+'/get_chain')
            print(response)
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    def find_all_transaction(self, account_number):
        transaction = []
        amount = 100
        for block in self.chain:
            for i in block['transactions']:
                if i['receiver'] == account_number:
                    amount += i['amount']
                    transaction.append({'timestamp': i['timestamp'],
                                        'sender': i['sender'],
                                        'receiver': i['receiver'],
                                        'amount': i['amount'],
                                        'status': 'received'
                                        })
                elif i['sender'] == account_number:
                    amount -= i['amount']
                    transaction.append({'timestamp': i['timestamp'],
                                        'sender': i['sender'],
                                        'receiver': i['receiver'],
                                        'amount': i['amount'],
                                        'status': 'sent'
                                        })
        for i in self.transactions:
            if i['receiver'] == account_number:
                # amount += i['amount']
                transaction.append({'timestamp': str(datetime.datetime.now()),
                                    'sender': i['sender'],
                                    'receiver': i['receiver'],
                                    'amount': i['amount'],
                                    'status': 'pending'
                                    })
            elif i['sender'] == account_number:
                amount -= i['amount']
                transaction.append({'sender': i['sender'],
                                    'receiver': i['receiver'],
                                    'amount': i['amount'],
                                    'status': 'pending'
                                    })
        return transaction, amount

    def send_coin(self, sender, receiver, amount):
        if sender in self.accounts and receiver in self.accounts:
            if self.accounts[sender]['amount'] >= amount:
                self.transactions.append({'sender': sender,
                                          'receiver': receiver,
                                          'amount': amount})

        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_coin(self, account_number, amount):
        for i in self.accounts:
            if i['account_number'] == account_number:
                i['amount'] += amount
                return 1
        return 0






############
#creating a web app
##########
app = Flask(__name__)
##########
@app.route("/")
def index():
    return "Welcome"
######create an address for the node on port5000
node_address = str(uuid4()).replace('-','')

#creating a blockchain

blockchain = Blockchain()

#mining a new block

@app.route('/mine_block', methods= ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver='d1', amount=1)

    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congo u created a new block',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']
                }
    # print(response)
    return jsonify(response), 200

#getting full blockchain

@app.route('/get_chain', methods= ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

#checking is vaild
@app.route('/isvalid', methods=['GET'])
def isvalid():
    response = {'Blockchain Valid':blockchain.is_chain_valid(blockchain.chain)}
    return response, 200

#adding new transaction
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json(force=True)
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This block will be added to the Block {index}'}
    return jsonify(response), 201

########crypto######

# decentrailizing blockchain
# connecting new node
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json(force=True)
    nodes = json.get('nodes')
    if nodes is None:
        return 'No nodes', 400
    # print
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nde are now conneccted',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_replaced = blockchain.replace_chain()
    if is_replaced:
        response = {'message': 'The node had different chaons so the chain was replaced by the longest one',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All Good, The chain is the longest one',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200


#####################
#login##
@app.route('/login', methods=['POST'])
def login():
    creds = request.get_json(force=True)
    public_key = creds['public_key']
    private_key = creds['private_key']
    response = {}
    if public_key in blockchain.accounts:
        account = blockchain.accounts[public_key]
        if account['private_key'] == private_key:
            response['message'] = "logged in"
            response['account_number'] = account['account_number']
            # response['amount'] = account['amount']
            response['transactions'], response['amount'] = blockchain.find_all_transaction(account['account_number'])
        else:
            response['message'] = 'Wrong private key'
    else:
        response['message'] = 'Wrong public key'
    return jsonify(response)

@app.route('/send_coin', methods = ['POST'])
def send_coin():
    json = request.get_json(force=True)
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'some elements of the transaction are missing', 400
    index = blockchain.send_coin(json['sender'], json['receiver'], json['amount'])
    # response = {'message': f'This block will be added to the Block {index}'}
    transaction, amount = blockchain.find_all_transaction(json['sender'])
    response = {
        'amount': amount,
        'transactions': transaction
    }
    return jsonify(response), 201

@app.route('/get_all_transactions', methods=['POST'])
def get_all_trnsaction():
    json = request.get_json(force=True)
    transaction, amount = blockchain.find_all_transaction(json['account_number'])
    response = {
        'amount': amount,
        'transactions': transaction
    }
    return jsonify(response), 201


@app.route('/add_coin', methods= ['POST'])
def add_coin():
    json = request.get_json(force=True)
    transaction_keys = ['account_number', 'amount']
    blockchain.add_transaction('', json['account_number'], json['amount'])
    transaction, amount = blockchain.find_all_transaction(json['sender'])
    response = {
        'amount': amount,
        'transactions': transaction
    }
    return jsonify(response), 201



@app.route('/generate_key', methods=['POST'])
def generate_key():
    req = request.get_json(force=True)
    public_key = req['public_key']
    passphrase = req['phrase']
    private_key = None
    response = {'private_key':private_key}
    return jsonify(response),  200

@app.route('/join_network', methods=['GET'])
def join_network():
    public_key = None
    response = {'public_key': public_key}
    return jsonify(response), 200





#runnig the webapp
# host, port = '0.0.0.0', 5004
# mine_block()
if __name__ == '__main__':
    app.run()






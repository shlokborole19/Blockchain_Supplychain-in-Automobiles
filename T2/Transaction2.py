# -*- coding: utf-8 -*-
"""
Created on Sun Nov 28 01:55:03 2021

@author: shlok
"""

### import the libraries
import datetime
import hashlib
import json
from flask import Flask,jsonify,request,redirect,url_for,render_template
import requests
from uuid import uuid4
from urllib.parse import urlparse

## PArt 1- Building the BlockChain

class SupplyChain:
    def __init__(self):
        self.chain=[]
        self.transactions=[]
        self.nodes=set()
        self.create_block(proof=1,previous_hash='0')
        
    def create_block(self,proof,previous_hash):
        block={'index':len(self.chain)+1,
               'timestamp':str(datetime.datetime.now()),
               'proof':proof,
               'previous_hash':previous_hash,
               'transactions':self.transactions
            
            }
        self.transactions=[]
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
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
    
    def add_transaction(self,serial_no,engine_no,chassis_no,model,v_category,colour,dealer_ID,dealer_name,transaction_date,payment_amount,payment_ID):
        self.transactions.append({
            'Serial No' : serial_no,
            'Engine No' : engine_no,
            'Chassis No': chassis_no,
            'Model Name' : model,
            'Vehicle Category': v_category,
            'Colour' : colour,
            'Dealer ID': dealer_ID,
            'Dealer Name' : dealer_name,
            'Transaction Date' : transaction_date,
            'Payment Amount' : payment_amount,
            'Payment ID' : payment_ID
            
            })
        previous_block=self.get_previous_block()
        return previous_block['index']+1
    
    def add_node(self,address):
        parsed_url=urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    ### consensus protocol
    
    def replace_chain(self):
        network=self.nodes
        longest_chain=None
        max_length=len(self.chain)
        
        for node in network:
            response=requests.get(f'http://{node}/get_chain')
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
        
            

## Part 2- Mining the BlockChain

app=Flask(__name__)

### creating an address for the node on Port 5000
node_address=str(uuid4()).replace('-','')

### Create The BlockChain
supplychain=SupplyChain()

@app.route("/")
def main():
    return render_template("main.html")
## Create a web app for the API
### Mining the new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = supplychain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = supplychain.proof_of_work(previous_proof)
    previous_hash = supplychain.hash(previous_block)
    #supplychain.add_transaction(serial_no = 'NA', engine_no = 'NA',model='NA',v_category='NA', chassis_no='NA', maf_batch='NA', maf_date='NA')
    block = supplychain.create_block(proof, previous_hash)
    t_chain = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return t_chain

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': supplychain.chain,
                'length': len(supplychain.chain)}
    #return jsonify(response), 200
    return response


# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = supplychain.is_chain_valid(supplychain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200


# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
#def add_transaction():
# =============================================================================
#     json = request.get_json()
#     transaction_keys = ['Serial No', 'Engine No', 'Chassis No','Model Name','Vehicle Category','Manufacturing Batch','Manufacturing Date']
#     if not all(key in json for key in transaction_keys):
#         return 'Some elements of the transaction are missing', 400
#     index = supplychain.add_transaction(json['Serial No'], json['Engine No'], json['Chassis No'],json['Model Name'],json['Vehicle Category'], json['Manufacturing Batch'],json['Manufacturing Date'])
#     response = {'message': f'This transaction will be added to Block {index}'}
#     return jsonify(response), 201
# =============================================================================

def form_supply():
        serial_no = request.form["form_serial_no"]
        engine_no = request.form["form_engine_no"]
        chassis_no = request.form["form_chassis_no"]
        model = request.form["form_model"]
        v_category = request.form["form_vehicle_cat"]
        colour = request.form["form_colour"]
        dealer_ID = request.form["form_dealer_id"]
        dealer_name = request.form["form_dealer_name"]
        transaction_date = request.form["form_t_date"]
        payment_amount = request.form["form_pay_amount"]
        payment_ID = request.form["form_pay_id"]
      
        params = {"Serial No" : serial_no, "Engine No" : engine_no, "Chassis No" : chassis_no , "Model Name" : model, 
        "Vehicle Category" : v_category, "Colour" : colour, "Dealer ID" : dealer_ID,"Dealer Name" : dealer_name,"Transaction Date" : transaction_date,"Payment Amount" : payment_amount,"Payment ID" : payment_ID}
        json = params
        transaction_keys = ['Serial No', 'Engine No', 'Chassis No','Model Name','Vehicle Category','Colour','Dealer ID','Dealer Name','Transaction Date','Payment Amount','Payment ID']
        if not all(key in json for key in transaction_keys):
            return 'Some elements of the transaction are missing', 400
        index = supplychain.add_transaction(json['Serial No'], json['Engine No'], json['Chassis No'],json['Model Name'], json['Vehicle Category'], json['Colour'],json['Dealer ID'],json['Dealer Name'],json['Transaction Date'],json['Payment Amount'],json['Payment ID'])
        response = {'message': f'This transaction will be added to Block {index}'}
        return redirect(url_for('mine_block'))

# Part 3 - Decentralizing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        supplychain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Blockchain now contains the following nodes:',
                'total_nodes': list(supplychain.nodes)}
    return jsonify(response), 201   

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = supplychain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': supplychain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': supplychain.chain}
    return jsonify(response), 200



# Running the app
# app.run(host = '0.0.0.0', port = 2001)
if __name__ == "__main__":
    app.run(debug=True)
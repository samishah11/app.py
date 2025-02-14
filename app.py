# The provided Python code sets up a Flask web application that integrates with the
#  Ethereum blockchain using the web3.py library. Here's a breakdown of its components



# 1. Import Statements:
from aiohttp import request
from flask import Flask, jsonify, render_template, session
from web3 import Web3
import requests
import json
# aiohttp is imported but not used in the code.
# Flask and related modules are used to create the web application and handle HTTP requests.
# Web3 from web3.py is used to interact with the Ethereum blockchain.
# requests is used for making HTTP requests, particularly to the CoinGecko API.
# json is used for handling JSON data.

# 2. Flask Application Setup:
app = Flask(__name__)
infura_url = 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'
web3 = Web3(Web3.HTTPProvider(infura_url))
app.config['SECRET_KEY'] = 'your-secret-key'  # replace with your secret key
# app initializes the Flask application.
# infura_url sets the URL for connecting to the Ethereum network via Infura.
# web3 establishes a connection to the Ethereum network using the provided Infura URL.
# SECRET_KEY is configured for session management in Flask.

# 3. Route Definitions:
# /new_account (GET):
@app.route('/new_account', methods=['GET'])
def new_account():
    account = web3.eth.account.create('YOUR_PASSWORD')
    session['account'] = {
        'privateKey': account.key.hex(),
        'address': account.address
    }
    return jsonify(session['account'])


with open('erc20_abi.json') as f:
    erc20_abi = json.load(f)

# Generates a new Ethereum account using a password.
# Stores the account's private key and address in the session.
# Returns the account details as a JSON response.
@app.route('/balance/<contract_address>', methods=['GET'])
def get_balance(contract_address):
    address = session.get('account').get('address')
    checksum_address = Web3.to_checksum_address(address)
    print(checksum_address)
    contract = web3.eth.contract(address=contract_address, abi=erc20_abi)
    balance = contract.functions.balanceOf(checksum_address).call()
    return jsonify({'balance': balance})


# Retrieves the balance of a specified ERC-20 token for the user's account.
# Requires the contract address of the ERC-20 token.
# Uses the ABI (erc20_abi) to interact with the token contract.
@app.route('/send_transaction', methods=['POST'])
def send_transaction():
    data = request.get_json()
    nonce = web3.eth.getTransactionCount(session['account']['address'])
    txn_dict = {
            'to': data['to'],
            'value': web3.toWei(data['amount'], 'ether'),
            'gas': 2000000,
            'gasPrice': web3.toWei('40', 'gwei'),
            'nonce': nonce,
            'chainId': 3
    }
    signed_txn = web3.eth.account.signTransaction(txn_dict, session['account']['privateKey'])
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return jsonify({'transaction_hash': txn_hash.hex()})


# Facilitates sending Ether from the user's account to another address.
# Accepts a JSON payload with the recipient's address and the amount to send.
# Signs and sends the transaction, returning the transaction hash.
@app.route('/market_chart/<contract_address>/<days>', methods=['GET'])
def get_market_chart(contract_address, days):
    api_key = 'coingecko_api_key' # replace this with your own API key
    response = requests.get(f'https://api.coingecko.com/api/v3/coins/ethereum/contract/{contract_address}/market_chart?vs_currency=usd&days={days}&api_key={api_key}')
    market_chart = response.json()
    return jsonify(market_chart)


# Fetches historical market data for a specified ERC-20 token using the CoinGecko API.
# Requires the contract address of the token and the number of days for historical data.
# Returns the market chart data as a JSON response.
@app.route('/')
def home():
    return render_template('index.html')


# Renders the index.html template for the home page.
# 4. Running the Application:
if __name__ == '__main__':
    app.run(debug=True)
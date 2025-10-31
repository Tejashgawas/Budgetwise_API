import click
import os
import requests
import json

API_URL = 'http://127.0.0.1:5000'
TOKEN_FILE = ".budgetwise_token"

@click.group()
def transactions():
    """Transactions relation command list"""
    pass

# -------------------------------------------------------
# LIST TRANSACTIONS
# -------------------------------------------------------

# @transactions.command()
# def list():

#     if not os.path.exists(TOKEN_FILE):
#         print("✗ no user currently logged in")
#         return
    
#     with open(TOKEN_FILE,'r') as f:
#         token = f.read().strip()
#         f.close
    
#     headers = {"Authorization":f"Bearer {token}"}
#     url = f"{API_URL}/api/transactions/list"
#     try:
#         response = requests.get(url, headers = headers)
#         print(json.dumps(response.json(), indent = 2))
#     except Exception as e:
#         print(f"✗ Error: {e}")

#--------------------------------------------------------------
# CREATE TRANSACTION
# -------------------------------------------------------------

@transactions.command(name = 'log-transaction')
@click.option('--amount', prompt = True, type = float, help = 'Transaction amount')
@click.option('--type', prompt = True, help='Type of trasaction either expense or income')
@click.option('--category_name', prompt=True, help='category of transaction eg:- movies, Groceries')
@click.option('--description', prompt = True, help='it can be name of items bought')

def add_transaction(amount, type, category_name, description):
    # checking if a user is logged in
    if not os.path.exists(TOKEN_FILE):
        print('✗ no user is currently logged in')
        return
    
    with open(TOKEN_FILE, 'r') as f:
        token = f.read().strip()
        f.close

    headers = {
                'Authorization':f'bearer {token}',
                'content-type': 'application/json'
                }
    
    data = {
            'amount' : amount,
            'type' : type,
            'category_name' : category_name,
            'description' : description}
    
    url = f'{API_URL}/api/transactions/log-transaction'
    try:
        response = requests.post(url, headers = headers, json = data)
        print(json.dumps(response.json(), indent = 2))
    except Exception as e:
        print(f"✗ Error: {e}")


    
# --------------------------------------------------------------
# GET All Transactions (optional filters)
# --------------------------------------------------------------



# --------------------------------------------------------------
# GET Single Transaction by ID
# --------------------------------------------------------------



# --------------------------------------------------------------
# UPDATE Transaction
# --------------------------------------------------------------

# @transactions.command()
# @click.option('--amount', prompt = True, type = float, help = 'Transaction amount')
# @click.option('--description', prompt = True, help='it can be name of items bought')


# --------------------------------------------------------------
# DELETE Transaction
# --------------------------------------------------------------
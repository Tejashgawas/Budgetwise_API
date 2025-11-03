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
@transactions.command()
@click.option('--type', type=click.Choice(['income', 'expense']), prompt="Type (income/expense or leave blank)", default='', help="Filter by type")
@click.option('--category', prompt="Category (or leave blank)", default='', help="Filter by category name")
@click.option('--start_date', prompt="Start date (YYYY-MM-DD or leave blank)", default='', help="Filter by start date")
@click.option('--end_date', prompt="End date (YYYY-MM-DD or leave blank)", default='', help="Filter by end date")
def list(type, category, start_date, end_date):

    if not os.path.exists(TOKEN_FILE):
        print("No user Logged in")
        return
    
    with open(TOKEN_FILE, 'r') as f:
        token = f.read().strip()
        f.close()
    
    headers = {"Authorization" : f"Bearer {token}"}

    data = {}
    if type:
        data['type'] = type
    if category:
        data['category'] = category
    if start_date:
        data['start_date'] = start_date
    if end_date:
        data['end_date'] = end_date

    url = f"{API_URL}/api/transactions/"

    try:
        response = requests.get(url,params=data, headers = headers)

        if response.status_code != 200:
            print(f' error {response.status_code} : {response.text}')
            return
        
        res_json = response.json()

        if not res_json:
            print('No transaction found')
            return
        
        print("\n Transaction")
        print("-" * 50)
        transactions = res_json.get("transactions", [])
        if not transactions:
            print("No transactions found.")
            return
        for t in transactions:
            print(f"ID: {t['id']}")
            print(f"Amount: {t['amount']}")
            print(f"Type: {t['type']}")
            print(f"Category: {t['category']}")
            print(f"Description: {t['description']}")
            print(f"Date: {t['date']}")
            print("-" * 50)

    except Exception as e:
        print(f'Error: {e}')


# --------------------------------------------------------------
# GET Single Transaction by ID
# --------------------------------------------------------------
@transactions.command(name = 'get_transaction')
@click.option('--transaction_id',prompt = True, help = "transaction id")

def get_transaction(transaction_id):

    if not os.path.exists(TOKEN_FILE):
        print('Please login')
        return
    
    with open(TOKEN_FILE,'r') as f:
        token = f.read().strip()
        f.close()
    
    headers = {"Authorization" : f"Bearer {token}"}

    url = f'{API_URL}/api/transactions/{transaction_id}'

    try: 
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f' error {response.status_code} : {response.text}')
            return
        
        res_json = response.json()
        

        if not res_json:
            print('No transaction found')
            return
        
        print("\n Transaction")
        print("-" * 50)
        print(f"ID: {res_json['id']}")
        print(f"Amount: {res_json['amount']}")
        print(f"Type: {res_json['type']}")
        print(f"Category: {res_json['category']}")
        print(f"Description: {res_json['description']}")
        print(f"Date: {res_json['date']}")
        print("-" * 50)

    except Exception as e:
        print(f'Error: {e}')

# --------------------------------------------------------------
# UPDATE Transaction
# --------------------------------------------------------------

@transactions.command()
@click.option('--amount', prompt = True, type = float, help = 'Transaction amount')
@click.option('--description', prompt = True, help='it can be name of items bought')
@click.option('--transaction_id', prompt = True, help='it can be name of items bought')

def updatetransaction(amount,description,transaction_id):

    if not os.path.exists(TOKEN_FILE):
        print("✗ no user currently logged in")
        return
    
    with open(TOKEN_FILE,'r') as f:
        token = f.read().strip()
        f.close
    
    headers = {
                "Authorization":f"Bearer {token}",
                "content-type": 'application/json'
            }

    data = {}
    if amount:
        data['amount'] = amount
    if description:
        data['description'] = description

    url = f'{API_URL}/api/transactions/{transaction_id}'
    try:
        response = requests.put(url, json=data, headers=headers)
        
        # ✅ Use response.json() to read returned data
        if response.status_code == 200:
            print("✓ Transaction updated successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(response.json())

    except Exception as e:
        print(f'Error: {e}')



# --------------------------------------------------------------
# DELETE Transaction
# --------------------------------------------------------------

@transactions.command(name = 'delete_transaction')
@click.option('--transaction_id', prompt=True,help='Transaction id u want to deete')

def delete_transaction(transaction_id):

    if not os.path.exists(TOKEN_FILE):
        print('Please login First')
        return
    
    with open(TOKEN_FILE, 'r') as f:
        token = f.read().strip()

    headers = {
            'Authorization' : f'Bearer {token}'
    }

    url = f'{API_URL}/api/transactions/{transaction_id}'
    try:
        response = requests.delete(url, headers=headers)
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")
import os
import requests
import json
import click

@click.group()
def categories():
    pass

API_URL = 'http://127.0.0.1:5000'
TOKEN_FILE = '.budgetwise_token'

# ----------------------------------------------------------
# CREATE CATEGORY
# ----------------------------------------------------------

@categories.command(name = 'add_category')
@click.option('--type', prompt = True, help='enter the type of category either expense or income')
@click.option('--name',prompt = True, help='enter the name of the category')

def add_category(type, name):

    if not os.path.exists(TOKEN_FILE):
        print("USer not logged in")
        return
    
    with open(TOKEN_FILE,'r') as f:
        token = f.read().strip()
        f.close()

    data = {'type' : type, 'name' : name}
    

    headers = {'Authorization' : f'Bearer {token}'}

    url = f"{API_URL}/api/categories/"

    try:
        response = requests.post(url,json = data, headers = headers)
        print(json.dumps(response.json(),indent=2))

    except Exception as e:
        print(f'error: {e}')


# ----------------------------------------------------------
# GET ALL CATEGORIES
# ----------------------------------------------------------

@categories.command(name="get_categories")
def get_categories():

    if not os.path.exists(TOKEN_FILE):
        print('No user is logged in')
        return
    
    with open(TOKEN_FILE,'r') as f:
        token = f.read().strip()
        f.close()

    headers = {'Authorization' : f'Bearer {token}'}

    url = f"{API_URL}/api/categories/"

    try:
        response = requests.get(url, headers = headers)
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f'Error: {e}')

#----------------------------------------------------------------
# GET CATEGORY (id-specific)
#----------------------------------------------------------------

@categories.command(name = 'categorybyId')
@click.option('--category_id', prompt=True, help='id of the category you want to see')

def categorybyId(category_id):

    if not os.path.exists(TOKEN_FILE):
        print("No user is currently logged in")
        return
    
    with open(TOKEN_FILE,'r') as f:
        token = f.read().strip()
        f.close()

    headers = {'Authorization' : f'Bearer {token}'}

    url = f'{API_URL}/api/categories/{category_id}'

    try:
        response = requests.get(url, headers = headers)
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f'error: {e}')

# -----------------------------------------------------------------
# update Category
# -----------------------------------------------------------------

@categories.command(name = 'update_category')
@click.option('--category_id', prompt=True, help='category id to update category')
@click.option('--name', prompt=True, help='name of the category')
@click.option('--type', prompt=True, help='type of category either expense or income')

def update_category(category_id, name, type):

    if not os.path.exists(TOKEN_FILE):
        print('No user has logged in')
        return
    
    with open(TOKEN_FILE, 'r') as f:
        token = f.read().strip()
        f.close()

    headers = {'Authorization' : f'Bearer {token}'}

    data = {'name': name, 'type' : type}

    url = f'{API_URL}/api/categories/{category_id}'

    try:
        response = requests.put(url, json = data, headers = headers)
        print(json.dumps(response.json(), indent=2))
    
    except Exception as e:
        print(f'Error : {e}')


#------------------------------------------------------
# Delete category
#-----------------------------------------------------

@categories.command(name='del_category')
@click.option('--category_id',prompt = True, help='Category id of the category u want to delete')

def del_category(category_id):
    if not os.path.exists(TOKEN_FILE):
        print('no user is logged in')
        return
    
    with open(TOKEN_FILE,'r') as f:
        token = f.read().strip()
        f.close()

    headers = {'Authorization' : f'Bearer {token}'}

    url = f'{API_URL}/api/categories/{category_id}'

    try: 
        response = requests.delete(url, headers=headers)
        print(json.dumps(response.json(),indent=2))

    except Exception as e:
        print(f'Error: {e}')
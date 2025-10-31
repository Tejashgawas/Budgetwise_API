#auth_commands.py
import click
import requests
import json
import os

API_URL = 'http://127.0.0.1:5000'
TOKEN_FILE = ".budgetwise_token"

@click.group()
def auth():
    """Authentication commands: register, login, logout,and view current user"""
    pass

# --------------------------------------------------------
# Register
# --------------------------------------------------------
@auth.command()
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--username', prompt=True)

def register(email, password, username):
    """Register a new user."""
    url = f"{API_URL}/api/auth/register"
    data = {"email": email, "password": password, "username": username}
    try:
        response = requests.post(url, json=data)
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")


# ----------------------------------------------------------
# LOGIN
# ----------------------------------------------------------

@auth.command()
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True)

def login(email, password):
    """User Login"""
    url = f'{API_URL}/api/auth/login'
    data = {"email" : email, "password": password}
    try:
        response = requests.post(url, json = data)
        res_json = response.json()

        if response.status_code == 200 and 'token' in res_json:
            with open(TOKEN_FILE, 'w') as f:
                f.write(res_json['token'])
            print('✅ logged in successfully')
        else:
            print('❌ Login failed: ', res_json)

    except Exception as e:
        print(f"❌ Error: {e}")

# ---------------------------------------------------------------------------------
# Current User
# ---------------------------------------------------------------------------------

@auth.command(name = 'me')
def current_user():

    # View the currently logged in user
    if not os.path.exists(TOKEN_FILE):
        print("✗ no User is logged in")
        return

    with open(TOKEN_FILE,'r') as f:
        token = f.read().strip()

    headers = {"Authorization" : f"Bearer {token}"}
    url = f'{API_URL}/api/auth/me'

    try: 
        response = requests.get(url, headers = headers)
        print(json.dumps(response.json(), indent = 2))

    except Exception as e:
        print(f"✗ Error: {e}")

#------------------------------------------------------------------------------------
# LOGOUT

@auth.command()
def logout():

    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print("✓ User logged out successfully")
    else:
        print("No token found to log user out")
    

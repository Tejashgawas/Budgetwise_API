#utils.py
import requests
import json
import os

#Base URL of your flask
API_URL = 'http://127.0.0.1:5000'

#file where token will be saved locally
TOKEN_FILE = ".budgetwise_token"

# ----------------------------------------------------------------------
#  Helper: API requests to Flask endpoints
#-----------------------------------------------------------------------

def api_request(method, endpoint, data=None, token=None):
    """
    Send an HTTP request to the Budgetwise API
    Handles headers, to token authentication, and JSON responses.
    """
    url = f"{API_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    # Include token if available (for authenticated routes)
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(method, url, json=data, headers=headers)
        response.raise_for_status()  # Raise an error for 4xx or 5xx responses

        # Try to parse the response as JSON
        return response.json()
    except requests.exceptions.RequestException as e:
        # Covers network issues or bad responses
        return {"error": str(e)}
    except ValueError:
        # Covers non-JSON responses
        return {"error": "Invalid response from server"}


# -------------------------------------------------------------
# Token Management
# -------------------------------------------------------------
def save_token(token):
    """
    Save JWT token locally after successful login.
    """
    with open(TOKEN_FILE, "w") as f:
        f.write(token)


def get_token():
    """
    Retrieve the saved token, if it exists.
    """
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None


def delete_token():
    """
    Delete the stored token (used during logout).
    """
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


# -------------------------------------------------------------
# Helper: Print API response in a readable format
# -------------------------------------------------------------
def print_response(response):
    """
    Display API responses nicely in the CLI.
    """
    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        print(json.dumps(response, indent=2))
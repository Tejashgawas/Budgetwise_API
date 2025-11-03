import os
import requests
import json
import click

API_URL = 'http://127.0.0.1:5000'
TOKEN_FILE = '.budgetwise_token'

@click.group()
def summary():
    pass

@summary.command()
@click.option('--period_type', prompt='period_type (or leave blank)', default='', help='Filter by period type')
@click.option('--period_value', prompt='perriod_value (or leave blank)',default='', help='filter by period value')
@click.option('--txt_type',prompt="txt_type (or leave blank)",default='',help='filter by text type')
@click.option('--start_date',prompt='start_date (YYYY-MM-DD or leave blank)',default='',help='filter by start date')
@click.option('--end_date',prompt='end_date (YYYY-MM-DD or leave blank)',default='',help='filter by end date')

def period(period_type,period_value,txt_type,start_date,end_date):

    if not os.path.exists(TOKEN_FILE):
        print('No user is logged in')
        return
    
    with open(TOKEN_FILE,'r')as f:
        token = f.read().strip()
        f.close()

    data = {}
    if period_type:
        data['period_type'] = period_type
    if period_value:
        data['period_value'] = period_value
    if txt_type:
        data['txt_type'] = txt_type
    if start_date:
        data['start_date'] = start_date
    if end_date:
        data['end_date'] = end_date

    headers = {'Authorization' : f'Bearer {token}'}

    url = f'{API_URL}/api/summary/period'

    try:
        response = requests.get(url, params=data, headers = headers)
        print(json.dumps(response.json(),indent=2))

    except Exception as e:
        print(f'Error : {e}')

@summary.command()
@click.option('--period_type', prompt='period_type (or leave blank)', default='', help='Filter by period type')
@click.option('--period_value', prompt='perriod_value (or leave blank)',default='', help='filter by period value')
@click.option('--txt_type',prompt="txt_type (or leave blank)",default='',help='filter by text type')
@click.option('--start_date',prompt='start_date (YYYY-MM-DD or leave blank)',default='',help='filter by start date')
@click.option('--end_date',prompt='end_date (YYYY-MM-DD or leave blank)',default='',help='filter by end date')
@click.option('--subcategory',prompt='subcategory or leave blank', default='',help='filter by category name')

def subcategory(period_type,period_value,txt_type,start_date,end_date,subcategory):

    if not os.path.exists(TOKEN_FILE):
        print('No user is logged in')
        return
    
    with open(TOKEN_FILE,'r')as f:
        token = f.read().strip()
        f.close()

    data = {}
    if period_type:
        data['period_type'] = period_type
    if period_value:
        data['period_value'] = period_value
    if txt_type:
        data['txt_type'] = txt_type
    if start_date:
        data['start_date'] = start_date
    if end_date:
        data['end_date'] = end_date
    if subcategory:
        data['subcategory'] = subcategory

    headers = {'Authorization' : f'Bearer {token}'}

    url = f'{API_URL}/api/summary/subcategory'

    try:
        response = requests.get(url, params=data, headers = headers)
        print(json.dumps(response.json(),indent=2))

    except Exception as e:
        print(f'Error : {e}')

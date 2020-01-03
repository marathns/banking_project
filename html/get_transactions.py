import plaid
import json
import time
import os,sys,inspect
from plaid import Client as PlaidClient
import config as Config
# import json_to_text as jt

def get_source_transactions(start_date,end_date):

    # token_file = os.getenv('token_file')
    token_file = Config.token_file

    def access_transactions(client_id,secret_key,public_key,env,access_token,str_date,end_date):
        plaid_client =  PlaidClient(client_id = client_id, secret=secret_key,
                          public_key=public_key, environment=env, api_version='2019-05-29',suppress_warnings = True)
        def get_trans(access_token : str,str_date:str, end_date:str):
            return plaid_client.Transactions.get(access_token,str_date,end_date)
        trans = get_trans(access_token,str_date,end_date)
        return trans

    with open(token_file) as f:

        PLAID_CLIENT_ID = f.readline().strip('\n').split(' = ')[1].lstrip("'").rstrip("'")
        PLAID_PUBLIC_KEY = f.readline().strip('\n').split(' = ')[1].lstrip("'").rstrip("'")
        PLAID_SECRET = f.readline().strip('\n').split(' = ')[1].lstrip("'").rstrip("'")
        PLAID_ENV = f.readline().strip('\n').split(' = ')[1].lstrip("'").rstrip("'")
        DISCOVER_ACCESS_TOKEN = f.readline().strip('\n').split(' = ')[1].lstrip("'").rstrip("'")
        AMEX_ACCESS_TOKEN = f.readline().strip('\n').split(' = ')[1].lstrip("'").rstrip("'")

        acc_tokens = {}
        acc_tokens['DISCOVER_ACCESS_TOKEN'] = DISCOVER_ACCESS_TOKEN
        acc_tokens['AMEX_ACCESS_TOKEN'] = AMEX_ACCESS_TOKEN

    for i in acc_tokens:
        trans = access_transactions(PLAID_CLIENT_ID,PLAID_SECRET,PLAID_PUBLIC_KEY,PLAID_ENV,acc_tokens[i],start_date,end_date)
        curr_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        parent_dir = os.path.dirname(curr_dir)
        file_dir = os.path.join(parent_dir,'json_files')
        with open(os.path.join(file_dir,'trans_'+str(i).split('_')[0]+'.json'),'w') as f:
            json.dump(trans,f)
            # print('The '+str(i).split('_')[0]+' transactions have been downloaded')

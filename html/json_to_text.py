import json
import pandas as pd
import jsonpickle
import os,sys,inspect

def json_text():
    curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    parent_dir = os.path.dirname(curr_dir)
    json_dir = os.path.join(parent_dir,'json_files')
    # # curr_dir = os.get
    df = pd.DataFrame()
    files = []
    for file in os.listdir(json_dir):
        if file.endswith(".json"):
            if 'AMEX' in file or 'DISCOVER' in file:
                files.append(os.path.join(json_dir,file))

    for file in files:

        with open(file,'r') as f:
            json_file = json.load(f)
            json_trans = json_file['transactions']

        account_id = []
        account_owner = []
        amount = []
        old_category = []
        category_id = []
        date = []
        name = []
        pending = []
        pending_transaction_id = []
        transaction_id = []
        acc_type = []
        #
        for trans in json_trans:
            # trans = jsonpickle.decode(trans)
            account_id.append(trans['account_id'])
            account_owner.append(trans['account_owner'])
            amount.append(trans['amount'])
            old_category.append(trans['category'])
            category_id.append(trans['category_id'])
            date.append(trans['date'])
            name.append(trans['name'])
            pending.append(trans['pending'])
            pending_transaction_id.append(trans['pending_transaction_id'])
            transaction_id.append(trans['transaction_id'])
            if 'AMEX' in file:
                trans['ACC_TYPE'] = 'AMEX'
            elif 'DISCOVER' in file:
                trans['ACC_TYPE'] = 'DISCOVER'
            acc_type.append(trans['ACC_TYPE'])

        d = {   'transaction_id':transaction_id,
                'date':date,
                'account_id':account_id,
                'account_owner':account_owner,
                'amount':amount,
                'old_category':old_category,
                'name':name,
                'acc_type':acc_type,
                'pending':pending}

        df1 = pd.DataFrame(data = d)

        df = df.append(df1,ignore_index = True)

        # print('The data has been appended')

    df['actual_amount'] = df['amount']
    df['category'] = ''
    file_dir = os.path.join(parent_dir,'txt_files')
    file = os.path.join(file_dir,'trans_file.txt')
    pending = ['False']
    df_trans = df[df.pending == False]
    df_trans.to_csv(file, sep = '|', index = False,header = False)
    print('The text file has been created')

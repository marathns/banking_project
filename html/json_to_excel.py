import json
import pandas as pd
import jsonpickle

with open('new_amex_trans.json','r') as f:
    json_file = json.load(f)
    # json_trans = json_file['transactions']
    json_trans = json_file
# print(type(json_trans))
# print(json_trans)
# print(len(json_trans))

# for i in json_trans:
#     print(i)
#     json_list = []
#     for t in json_file['transactions']:
#         json_list.append(jsonpickle.encode(t._json,unpicklable = False))
#
account_id = []
account_owner = []
amount = []
category = []
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
    category.append(trans['category'])
    category_id.append(trans['category_id'])
    date.append(trans['date'])
    name.append(trans['name'])
    pending.append(trans['pending'])
    pending_transaction_id.append(trans['pending_transaction_id'])
    transaction_id.append(trans['transaction_id'])
    acc_type.append(trans['ACC_TYPE'])


d = {   'transaction_id':transaction_id,
        'date':date,
        'account_id':account_id,
        'account_owner':account_owner,
        'amount':amount,
        'category':category,
        'name':name,
        'acc_type':acc_type,
        'pending':pending}

df = pd.DataFrame(data = d)

df.to_csv('test_df_amex.txt',sep='|', index = False, header=False)

print('The file has been downloaded')
# print(account_id)

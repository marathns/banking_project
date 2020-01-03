import pandas as pd
import os,sys,inspect
import hashlib
import sqlite3

def after_db():
    def sql_query(query,conn):
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return rows

    curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    parent_dir = os.path.dirname(curr_dir)
    db_path = os.path.join(parent_dir,'test.db')
    conn = sqlite3.connect(db_path)

    file_path = os.path.join(curr_dir,'ML','expenses_ml_test - Copy.csv')
    df = pd.read_csv(file_path,encoding='utf-8')
    df = df[pd.notnull(df.Particulars)]
    # df.ID = df.ID.astype(int)

    # results = sql_query('select distinct transaction_id from transactions',conn)
    rows = sql_query('select transaction_id,tran_date,tran_particulars,category from transactions',conn)
    data_list = []

    df1 = pd.DataFrame()

    update = 0

    for i in rows:
        if i[0] not in list(df.ID.values):
            data_list.append(list(i))
        else:
            if df.loc[df['ID'] == i[0]]['hash_val'].values == hashlib.sha1(str(i[0]+i[1]+i[2]+i[3]).encode('utf-8')).hexdigest():
                pass
            else:
                update += 1
                df.set_value(df.loc[df['ID'] == i[0]].index,'hash_val',hashlib.sha1(str(i[0]+i[1]+i[2]+i[3]).encode('utf-8')).hexdigest())
                df.set_value(df.loc[df['ID'] == i[0]].index,'Category',i[3])
                print(hashlib.sha1(str(i[0]+i[1]+i[2]+i[3]).encode('utf-8')).hexdigest())

    result = ''
    result1 = ''
    # if update > 0:
    #     df.to_csv(file_path,index=False)
    #     result = '{} records updated with new categories'.format(update)

    # print(df1)

    if len(data_list) > 0:
        for i in data_list:
            i.append(hashlib.sha1(str(i[0]+i[1]+i[2]+i[3]).encode('utf-8')).hexdigest())
        df = pd.DataFrame(data_list)
        df.to_csv(file_path,mode = 'a',index=False,header=False)
        result = 'Records appended to the file'
        if update > 0:
            df.to_csv(file_path,index=False)
            result1 = result + ' and ' + '{} records updated with new categories'.format(update)
        else:
            result1 = result
    else:
        if update > 0:
            df.to_csv(file_path,index=False)
            result1 =  '{} records updated with new categories'.format(update)
        else:
            result1 = 'No new records to be appended'

    return result1
# df_db['hash_col'] = (df['Date'] + df['Particulars'] + df['Category'] + df['Source']).apply(hash)
#
# df1 = pd.DataFrame(data = df_db)
# df_db_test = pd.DataFrame()
# df_db_test = df_db_test.append(df1,ignore_index = True)
# df_db_test.to_csv('test_hash.txt')

# results = sql_query("select * from transactions where tran_date between '{}' and '{}'".format('2019-01-01','2019-01-05'))
# for i in results:
#     print(i)

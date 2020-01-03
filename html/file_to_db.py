import sqlite3
import pandas
import os,sys,inspect
import csv

def file_db(file_path):
    curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    parent_dir = os.path.dirname(curr_dir)
    db_path = os.path.join(parent_dir,'test.db')

    conn = sqlite3.connect(db_path)
    data = []
    # file = os.path.join(parent_dir,'txt_files','trans_file.txt')
    file = file_path
    with open(file,'r') as f:
        file_lines = f.readlines()
        if len(data) == 0:
            for row in file_lines:
                data.append(row.rstrip('\n').split('|'))

    def get_trans(conn):
        sql_query = 'select distinct transaction_id from transactions'
        c = conn.cursor()
        c.execute(sql_query)
        results = c.fetchall()
        return results


    results = get_trans(conn)
    c = conn.cursor()

    old_counter = 0
    new_counter = 0
    for i in data:
        if i[0] in [j[0] for j in results]:
            old_counter += 1
            pass
        else:
            new_counter += 1
            sql_query = ('INSERT INTO TRANSACTIONS values ("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(i[0],i[1],i[2],i[3],i[4],i[6],i[7],i[9],i[10]))
            c.execute(sql_query)
    conn.commit()
    conn.close()

    if old_counter > 0 and new_counter == 0:
        return ('Data already present in the database')
    elif old_counter > 0 and new_counter > 0:
        return ("{} transactions already in the database and {} new transactions inserted".format(old_counter,new_counter))
    elif old_counter == 0 and new_counter >0:
        return ("{} new transactions inserted in the database".format(new_counter))

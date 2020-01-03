import sqlite3
import pandas as pd
import os

# if os.path.exists('sample.db'):
	# os.remove('sample.db')

# conn = sqlite3.connect('sample.db', check_same_thread = False)

headers = ['Serial','Transaction_ID','Date','Particulars','Amount','Actual_Amount','Account']
data_table = pd.read_csv(r'C:\Users\maratn1\Documents\Python\flask_proj\test_db.csv', header=None, names = headers)

conn = sqlite3.connect('sample.db', check_same_thread = False)
c = conn.cursor()

c.execute("select count(name) from sqlite_master where type='table' and name = 'data_table'")

if c.fetchone()[0] == 1:
	c.execute('SELECT DISTINCT SERIAL from data_table')
	trans = c.fetchall()
	old_trans = []
	for i in trans:
		old_trans.append(i[0])

	data_table_new = data_table[~data_table['Serial'].isin(old_trans)]
	if len(data_table_new) != 0:

		for index, row in data_table_new.iterrows():
			conn.execute('Insert into data_table(Serial,Transaction_ID, Date, Particulars, Amount, Actual_Amount, Account) values (?,?,?,?,?,?,?)',[row[0],row[1],row[2],row[3],row[4],row[5],row[6]])
			# print([row[0],row[1],row[2],row[3],row[4],row[5],row[6]])
	else:
		print('There is no new data')
	conn.commit()
else:
	data_table.to_sql('data_table',conn,dtype={
	'Serial':'INTEGER',
	'Transaction_ID':'VARCHAR(100)',
	'Date':'DATE',
	'Particulars':'VARCHAR(100)',
	'Amount':'DECIMAL(10,2)',
	'Actual_Amount':'DECIMAL(10,2)',
	'Account':'VARCHAR(10)'
	})

conn.row_factory = sqlite3.Row

def sql_query(query):
	cur = conn.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	return rows

def sql_query_new(query,var):
	cur = conn.cursor()
	cur.execute(query,var)
	rows = cur.fetchall()
	return rows

def get_dates(query):
	cur=conn.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	return rows

def sql_edit_insert(query,var):
	cur = conn.cursor()
	cur.execute(query,var)
	conn.commit()

def sql_delete(query,var):
	cur=conn.cursor()
	cur.execute(query,var)

def sql_query2(query,var):
	cur=conn.cursor()
	cur.execute(query,var)
	rows=cur.fetchall()
	return rows

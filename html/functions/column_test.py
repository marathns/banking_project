import pandas as pd
import sqlite3
import os

headers = ['Serial','Transaction_ID','Date','Particulars','Amount','Actual_Amount','Account']
data_table = pd.read_csv(r'C:\Users\maratn1\Documents\Python\flask_proj\test_db_2.csv', header=None, names = headers)

conn = sqlite3.connect('sample.db', check_same_thread = False)
c = conn.cursor()

# c.execute('drop table trans_test')
# c.execute('drop view myview')
# conn.commit()

def create_table(conn, query):

	c.execute(query)
	conn.commit()

def sql_query(conn, query):

	c.execute(query)
	rows = c.fetchall()
	return rows

def create_view(conn,query):
	c.execute(query)
	conn.commit()

query = ''' 
		create table if not exists trans_test 
		(Serial INTEGER,
		Transaction_ID VARCHAR(100),
		Date DATE,
		Particulars VARCHAR(100),
		Amount DECIMAL(10,2),
		Actual_Amount DECIMAL(10,2),
		Account VARCHAR(10))

		'''

c.execute("select count(name) from sqlite_master where type='table' and name = 'trans_test'")
tab_count =  c.fetchone()

if tab_count[0] != 1:
	create_table(conn, query)
else:
	print('The table already exists')

c.execute('select distinct serial from trans_test')
trans = c.fetchall()

ids = []
for i in trans:
	ids.append(i[0])
print(ids)
data_table_new = data_table[~data_table['Serial'].isin(ids)]
print(data_table_new)
if len(data_table_new) != 0:
	for index, row in data_table_new.iterrows():
		c.execute('Insert into trans_test(Serial,Transaction_ID, Date, Particulars, Amount, Actual_Amount, Account) values (?,?,?,?,?,?,?)',[row[0],row[1],row[2],row[3],row[4],row[5],row[6]])
			
check_view = c.execute("select count(name) from sqlite_master where type = 'view' and name = 'myview'")

if check_view.fetchone()[0] != 1:
	view = ''' create view myview as 
			select *, 
			cast(case when Actual_Amount is null then Amount
			else Actual_Amount end AS DECIMAL(10,2)) AS Final_Amt
			from trans_test '''			

	create_view(conn,view)
else:
	print('The view already exists')

view_results = c.execute('select * from myview')
v_results = view_results.fetchall()
for i in range(len(v_results)):
	print(v_results[i])

select_query = 'select * from trans_test'
results = sql_query(conn,select_query)

for i in range(len(results)):
	print(results[i])
conn.commit()
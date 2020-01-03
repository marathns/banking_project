import sqlite3
import pandas as pd
import os,sys,inspect

def after_db():
	curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
	parent_dir = os.path.dirname(curr_dir)
	db_path = os.path.join(parent_dir,'test.db')
	print(db_path)
	conn = sqlite3.connect(db_path)
	c = conn.cursor()

	file_path = os.path.join(curr_dir,'ML','expenses_ml_test.csv')
	df = pd.read_csv(file_path,encoding='utf-8')

	df = df[pd.notnull(df['Particulars'])]
	df_db = df[df.Source == 'DB']
	print(df_db)
	def sql_query(query):
		cur = conn.cursor()
		cur.execute(query)
		rows = cur.fetchall()
		return rows

	trans_list = []

	cols = c.execute('select * from transactions')
	names = list(map(lambda x:x[0], cols.description))

	c.execute('select max(tran_date) from transactions')
	results = c.fetchall()
	max_date_db = results[0][0]

	df_date = pd.DataFrame(columns = ['Date'])
	df_date['Date'] = pd.to_datetime(df_db['Date']).dt.date
	max_date = max(df_date['Date'])

	if len(df_db) == 0:
		results = sql_query('''select * from transactions''')
		for i in results:
			trans_list.append(list(i))
	elif len(df_db) != 0:
		max_date = max(pd.to_datetime(df_db['Date']).dt.date)
		if max_date_db != max_date:
			df_date = pd.DataFrame(columns = ['Date'])
			df_date['Date'] = pd.to_datetime(df_db['Date']).dt.date
			max_date = max(df_date['Date'])
			results = sql_query('''select * from transactions where tran_date > "{}"'''.format(max_date))
			for i in results:
				trans_list.append(list(i))
		else:
			print('Data already appended')
	trans_df = pd.DataFrame(trans_list, columns = names)
	new_trans_df = trans_df[['tran_date','tran_particulars','category']]
	new_trans_df['Source'] = 'DB'
	new_trans_df.columns = ['Date','Particulars','Category','Source']
	new_trans_df.to_csv(file_path,mode = 'a',header=False)
	print('Transactions added to the ML Model')

import pandas as pd
import sqlite3
import os

conn = sqlite3.connect('C:\\Users\\nmarathe\\PycharmProjects\\banking_project\\test.db', check_same_thread = False)
c = conn.cursor()

conn.row_factory = sqlite3.Row

def sql_query(query):
	cur = conn.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	return rows

# results = sql_query('Select * from data_table')
# for i in range(len(results)):
# 	print(results[i])

def sql_edit_insert(query,var):
	cur = conn.cursor()
	cur.execute(query,var)
	conn.commit()

def sql_insert(query):
	cur = conn.cursor()
	cur.execute(query)
	conn.commit()

def sql_delete(query,var):
	cur=conn.cursor()
	cur.execute(query,var)

def sql_query2(query,var):
	cur=conn.cursor()
	cur.execute(query,var)
	rows=cur.fetchall()
	return rows


# results = sql_query('select min(tran_date) from transactions')
# print(results)

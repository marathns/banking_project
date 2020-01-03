import pandas as pd
import numpy as np
from io import StringIO
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
import sqlite3
import re
import os,sys,inspect

def text_ml(file_path):
	curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
	parent_dir = os.path.dirname(curr_dir)
	db_path = os.path.join(parent_dir,'test.db')

	conn = sqlite3.connect(db_path)
	c = conn.cursor()

	def sql_query(query):
		cur = conn.cursor()
		cur.execute(query)
		rows = cur.fetchall()
		return rows

	ml_file = os.path.join(os.path.join(curr_dir,'ML'),'expenses_ml_test.csv')
	df = pd.read_csv(ml_file,encoding='utf-8')

	df = df[pd.notnull(df['Particulars'])]
	df['Particulars'] = df['Particulars'].map(lambda x:re.sub('[^A-Za-z0-9]+', ' ',x))

	col = ['Particulars','Category'] # define the required columns
	df = df[col] # subset the dataframe
	df = df[pd.notnull(df['Category'])] # remove the rows where category is null

	df['Category'] = df['Category'].str.lower() # convert categories to lower case

	df.columns = ['Particulars','Category']

	df['category_id'] = df['Category'].factorize()[0]
	category_id_df = df[['Category','category_id']].drop_duplicates().sort_values('category_id')

	category_to_id = dict(category_id_df.values)

	id_to_category = dict(category_id_df[['category_id','Category']].values)

	tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words='english')
	features = tfidf.fit_transform(df.Particulars).toarray()
	labels = df.category_id

	X_train, X_test, y_train, y_test = train_test_split(df['Particulars'], df['Category'], random_state = 0)
	count_vect = CountVectorizer()
	X_train_counts = count_vect.fit_transform(X_train)
	tfidf_transformer = TfidfTransformer()
	X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
	clf = MultinomialNB().fit(X_train_tfidf, y_train)

	# print(clf.predict(count_vect.transform(["kroger"])))
	# file_path = os.path.join(os.path.join(parent_dir,'txt_files'),'trans_file.txt')
	file_path = file_path
	data_file = pd.read_csv(file_path
	                        ,sep='|'
	                        ,names = ['tran_id','tran_date','acct_id','acct_name','amount','old_category','particulars','account','pending','actual_amount','category'])


	new_list = []
	for i in data_file['particulars']:
	    y = [i]
	    new_list.append([i, ''.join(map(str,clf.predict(count_vect.transform(y))))])

	new_df = pd.DataFrame(new_list,columns=['particulars','category'])

	data_file['category'] = new_df['category']

	data_file.to_csv(file_path,sep='|',header=False,index=False)
	print('File has been categorized')

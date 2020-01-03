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

conn = sqlite3.connect('C:\\Users\\nmarathe\\PycharmProjects\\banking_project\\test.db')
c = conn.cursor()

def sql_query(query):
	cur = conn.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	return rows

df = pd.read_csv('expenses_ml_test.csv',encoding='utf-8')

df = df[pd.notnull(df['Particulars'])]
df['Particulars'] = df['Particulars'].map(lambda x:re.sub('[^A-Za-z0-9]+', ' ',x))

date_col = ['Date']
df_date = df[date_col]
df_date = df_date[pd.notnull(df['Date'])]
df_date['Date'] = pd.to_datetime(df_date['Date']).dt.date

max_date = max(df_date['Date'])

# results = sql_query('''select * from transactions where tran_date > "{}"'''.format(max_date))
# print(len(results))
# if len(results) > 0:
#     new_data = []
#     for i in results:
#         new_data.append([i[1],i[5],i[8]])
#
#     new_data_df = pd.DataFrame(new_data,columns=['Date','Particulars','Category'])
#     new_data_df.to_csv('expenses_ml_test.csv',mode = 'a',header=False)

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
data_file = pd.read_csv('''C:\\Users\\nmarathe\\PycharmProjects\\banking_project\\txt_files\\trans_file.txt'''
                        ,sep='|'
                        ,names = ['tran_id','tran_date','acct_id','acct_name','amount','old_category','particulars','account','pending','actual_amount','category'])

new_list = []
for i in data_file['particulars']:
    y = [i]
    new_list.append([i, ''.join(map(str,clf.predict(count_vect.transform(y))))])

new_df = pd.DataFrame(new_list,columns=['particulars','category'])

data_file['category'] = new_df['category']

data_file.to_csv('''C:\\Users\\nmarathe\\PycharmProjects\\banking_project\\txt_files\\trans_file.txt''',sep='|',header=False,index=False)
print('File created')

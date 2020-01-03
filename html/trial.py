import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import os, inspect
import pandas as pd
import sqlite3

curr_dir = os.getcwd()
parent_dir = os.path.dirname(curr_dir)
db_path = os.path.join(parent_dir,'test.db')
conn = sqlite3.connect(db_path,check_same_thread = False)

cur = conn.cursor()
results = cur.execute("select * from transactions where category NOT IN ('payment', 'payments')")
names = list(map(lambda x:x[0], results.description))
rows = cur.fetchall()
results = []
for i in rows:
    results.append(list(i))
df = pd.DataFrame(results,columns = names)
# df['yearmonth'] = df['tran_date'].map(lambda x: 100*x.year + x.month)
df['yearmonth'] = df['tran_date'].apply(lambda x: x[:7])

def get_graph_dates(df,yearmonth):
    df1 = df[df['yearmonth'] == yearmonth]
    monthly_sales = df1.groupby('category')['actual_amount'].sum().reset_index()
    return monthly_sales

monthly_sales = get_graph_dates(df,'2019-02')
print(monthly_sales)
print(monthly_sales.shape)

import pandas as pd
from queries import sql_query
import os, sys, inspect
import sqlite3
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.io import show, output_file
from bokeh.plotting import figure
results = sql_query('select * from transactions')
results_list = []
for i in results:
    results_list.append(list(i))

curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
parent_dir = os.path.dirname(curr_dir)
db_path = os.path.join(parent_dir,'test.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()
cols = c.execute('select * from transactions')
names = list(map(lambda x:x[0], cols.description))

df = pd.DataFrame(data = results)
df.columns = names
df = df[df['category'] != 'payment']
# df['Year'] = pd.DatetimeIndex(df['tran_date']).year
# df['Month'] = pd.DatetimeIndex(df['tran_date']).month
df['YearMonth'] = pd.DatetimeIndex(df['tran_date']).year.map(str)+pd.DatetimeIndex(df['tran_date']).month.map(str)
df['category'] = df['category'].str.lower()

dates = df['YearMonth'].unique().tolist()
# print(dates)
# print(df.head())
categories = sorted(df['category'].unique().tolist())
yearmonths = sorted(df['YearMonth'].unique().tolist())

yrmonth = '20191'
cat = 'car fuel'
def append_dict(categories,df,yrmonth):
    ym = df[df['YearMonth'] == yrmonth].groupby('category')['actual_amount'].sum()
    for i in categories:
        if i.lower() not in ym.index:
            ym.loc[i] = 0.0

    ym = ym.sort_index()
    ym_values = ym.values.tolist()
    return ym_values


def cat_date_chart(categories,df,dates):
    new_dict = {'cats':categories}
    dates = dates
    for i in dates:
        new_dict[i] = []
        new_dict.update({i:append_dict(categories,df,i)})

    x = [ (category, yearmonth) for category in categories for yearmonth in dates]
    counts = sum(zip(new_dict['20191'],new_dict['20192']),())
    source = ColumnDataSource(data = dict(x=x, counts=counts))
    # print(x)
    print(counts)

def columndatasrctest(df,categories,dates,yrmonth,cat):

    x = []

    amnts = []
    for i in dates:
        ym = df[df['YearMonth'] == i].groupby('category',as_index=False)['actual_amount'].sum()
        val = ym[ym['category'] == 'car fuel'].actual_amount
        amnts.append(max(val))
        x.append((cat,i))
    # print(x)
    counts = tuple(amnts)
    source = ColumnDataSource(data = dict(x=x, counts=counts))

    p=figure(x_range = FactorRange(*x), plot_height = 550, plot_width = 500, title = "Amounts by categories", toolbar_location = None, tools = "hover", tooltips = "@x sum: @$name")
    p.vbar(x='x', top = 'counts', width = 0.9, source=source, name = "counts")

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xaxis.group_label_orientation = 'vertical'
    p.xgrid.grid_line_color = None
    return p
cat_date_chart(categories,df,dates)
columndatasrctest(df,categories,dates,yrmonth,cat)

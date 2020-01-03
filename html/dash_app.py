import os, sys,inspect

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
import plotly.graph_objs as go

import pandas as pd
from sqlalchemy import create_engine

import sqlite3

# curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
curr_dir = os.getcwd()
parent_dir = os.path.dirname(curr_dir)
db_path = os.path.join(parent_dir,'test.db')
# db_path = 'sqlite:///test.db'
conn = sqlite3.connect(db_path,check_same_thread = False)
print(curr_dir)
print(parent_dir)
print(db_path)
def fetch_data(q):
    df = pd.read_sql(
        sql=q,
        con=conn
    )
    return df

def sql_query(query,conn):
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    return rows

def get_dates():

    dates_query = (
        f'''
        select distinct yearmonth from
        (select strftime('%Y',tran_date) || '-' || strftime('%m',tran_date) as yearmonth from transactions)a
        '''
    )
    dates = sql_query(dates_query,conn)
    dates_list = []
    for i in dates:
        dates_list.append(list(i))
    dates = pd.DataFrame(dates_list, columns = ['yearmonth'])
    dates = list(dates['yearmonth'].sort_values(ascending=True))
    return dates

def get_categories(dates):
    '''Returns the seasons of the datbase store'''

    category_query = (
        f'''
        SELECT DISTINCT category
        FROM transactions
        WHERE strftime('%Y',tran_date) || '-' || strftime('%m',tran_date)='{dates}'
        '''
    )
    categories = sql_query(category_query,conn)
    cats_list = []
    for i in categories:
        cats_list.append(list(i))
    categories = pd.DataFrame(cats_list,columns = ['category'])
    categories = list(categories['category'].sort_values(ascending=False))
    return categories


def get_expense_results(dates, category):
    '''Returns match results for the selected prompts'''

    results_query = (
        f'''
        SELECT *
        FROM transactions
        WHERE strftime('%Y',tran_date) || '-' || strftime('%m',tran_date)='{dates}'
        AND category = '{category}'
        ORDER BY tran_date ASC
        '''
    )
    match_results = fetch_data(results_query)
    return match_results

#########################
# Dashboard Layout / View
#########################

def generate_table(dataframe, max_rows=10):
    return html.Table(

        [html.Tr([html.Th(col) for col in dataframe.columns])] +


        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


def onLoad_date_options():

    date_options = (
        [{'label': dates, 'value': dates}
         for dates in get_dates()]
    )
    return date_options

# Set up Dashboard and create layout
app = dash.Dash()
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

app.layout = html.Div([

    # Page Header
    html.Div([
        html.H1('Dashboard')
    ]),

    # Dropdown Grid
    html.Div([
        html.Div([
            # Select Division Dropdown
            html.Div([
                html.Div('Select Dates', className='three columns'),
                html.Div(dcc.Dropdown(id='date-selector',
                                      options=onLoad_date_options()),
                         className='nine columns')
            ]),

            # Select Season Dropdown
            html.Div([
                html.Div('Select Category', className='three columns'),
                html.Div(dcc.Dropdown(id='category-selector'),
                         className='nine columns')
            ]),

            # Select Team Dropdown
            # html.Div([
            #     html.Div('Select Account', className='three columns'),
            #     html.Div(dcc.Dropdown(id='acct-selector'),
            #              className='nine columns')
            # ]),
        ], className='six columns'),

        # Empty
        html.Div(className='six columns'),
    ], className='twleve columns'),

    # Match Results Grid
    html.Div([

        # Match Results Table
        html.Div(
            html.Table(id='expense-results'),
            className='six columns'
        ),

        # Season Summary Table and Graph
        # html.Div([
        #     # summary table
        #     dcc.Graph(id='season-summary'),
        #
        #     # graph
        #     dcc.Graph(id='season-graph')
        #     # style={},
        #
        # ], className='six columns')
    ]),
])


#############################################
# Interaction Between Components / Controller
#############################################

# Template
# Load Seasons in Dropdown
@app.callback(
    Output(component_id='category-selector', component_property='options'),
    [
        Input(component_id='date-selector', component_property='value')
    ]
)
def populate_category_selector(dates):
    categories = get_categories(dates)
    return [
        {'label': category, 'value': category}
        for category in categories
    ]

@app.callback(
    Output(component_id='expense-results', component_property='children'),
    [
        Input(component_id='date-selector', component_property='value'),
        Input(component_id='category-selector', component_property='value')
        # Input(component_id='team-selector', component_property='value')
    ]
)
def load_expense_results(dates, category):
    results = get_expense_results(dates, category)
    return generate_table(results, max_rows=50)

# start Flask server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='127.0.0.1',
        port=8050
    )

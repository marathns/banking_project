import sqlite3
import pandas as pd
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

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
# print(df.columns)

monthly_sales = df.groupby('yearmonth')['actual_amount'].sum().reset_index()
category_sales = df.groupby('category')['actual_amount'].sum().reset_index()

month_list = monthly_sales['yearmonth'].tolist()
month_values = monthly_sales['actual_amount'].tolist()

cat_list = category_sales['category'].tolist()
cat_values = category_sales['actual_amount'].tolist()

dd_list = []

for i in month_list:
    dd_dict = {}
    dd_dict['label'] = i
    dd_dict['value'] = i
    dd_list.append(dd_dict)

# dd_menu_item = [dbc.DropdownMenuItem(i) for i in month_list]
# print(dd_menu_item)
category_list = []
for i in cat_list:
    cat_dict = {}
    cat_dict['label'] = i
    cat_dict['value'] = i
    category_list.append(cat_dict)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'bars': '#222222'
}

def get_graph_dates(df,yearmonth):
    df1 = df[df['yearmonth'] == yearmonth]
    monthly_sales = df1.groupby('category')['actual_amount'].sum().reset_index()
    return monthly_sales

new_results = get_graph_dates(df,'2019-01')

trace1 = go.Bar(x = new_results['category'], y = new_results['actual_amount'],
                    name = 'Monthly Sales'
                )
layout = go.Layout(title = 'Monhtly Sales Bar Plot',
                   hovermode = 'closest',
                   )
fig = go.Figure(data = [trace1], layout = {
    'plot_bgcolor': colors['background'],
    'paper_bgcolor': colors['background'],
    'font': {
        'color': colors['text']
    }})

def get_graph_cats(df,category):
    df1 = df[df['category'] == category]
    cat_sales = df1.groupby('yearmonth')['actual_amount'].sum().reset_index()
    return cat_sales

cat_results = get_graph_cats(df,'rent')

trace2 = go.Bar(x = cat_results['yearmonth'], y = cat_results['actual_amount'],
                    name = 'Category Sales'
                )
layout = go.Layout(title = 'Monthly Sales per Category',
                   hovermode = 'closest',
                   )
fig1 = go.Figure(data = [trace2], layout = {
    'plot_bgcolor': colors['background'],
    'paper_bgcolor': colors['background'],
    'font': {
        'color': colors['text']
    }})


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H2(
        children='Expenses Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Dashboard to display expense sumamry', style={
        'textAlign': 'center',
        'color': '#ffa500'
    }),


    html.H3(children = 'Summary Graphs',
            style = {'textAlign': 'left',
                        'color' : '#ffa500'}),
        dcc.Graph(id = 'graph1',
                  figure = {
                  'data' : [go.Bar(x = month_list, y = month_values, name='Monthly_sales')],

                  'layout': {
                      'plot_bgcolor': colors['background'],
                      'paper_bgcolor': colors['background'],
                      'font': {
                          'color': colors['text']
                      }
                  }
                 },style = {'width': '50%', 'display':'inline-block'}
                ),
        dcc.Graph(id = 'graph2',
                    figure = {
                                'data':
                                        [go.Bar
                                                (x = cat_list, y=cat_values, name='Category_sales')],
                                'layout': {
                                    'plot_bgcolor': colors['background'],
                                    'paper_bgcolor': colors['background'],
                                    'font': {
                                        'color': colors['text']
                                    }
                                }
                            },style =  {'width': '50%', 'display':'inline-block'}
                    )
                    ,
        html.Div([html.H3(children = 'Enter start / end date:',
                          style = {'color' : '#ffa500'})],
        style =  {'width': '50%', 'display':'inline-block'}),

        html.Div([html.H3(children = 'Enter category:',
                          style = {'color' : '#ffa500'})],
        style =  {'width': '50%', 'display':'inline-block'}),

        html.Div([
        dcc.Dropdown(
            id='demo-dropdown-1',
            options=dd_list)],
            style =  {'width': '35%', 'display':'inline-block'}
            # value=dd_list[0]['2019-01']
        ),
        html.Div(style = {'width' : '15%', 'display':'inline-block'}),
        html.Div([
        dcc.Dropdown(
            id='demo-dropdown-2',
            options=category_list)],
            style =  {'width': '35%', 'display':'inline-block'}

        ),
        html.Div([
        dcc.Graph(id = 'graph3',
                 figure = fig)],
                 style = {'width':'50%', 'display':'inline-block'}),
        html.Div([
        dcc.Graph(id = 'graph4',
                 figure = fig1)],
                 style = {'width':'50%', 'display':'inline-block'}),
        html.Div(id='dd-output-container')
])

@app.callback(Output('graph3','figure'),
              [Input('demo-dropdown-1','value')])

def update_figure(input1):
    results = get_graph_dates(df,input1)
    trace1 = go.Bar(x = results['category'], y=results['actual_amount'],
                    name = 'Monthly_Sales'
                    )
    fig = go.Figure(data = [trace1],layout={
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['background'],
        'font': {
            'color': colors['text']
        }})
    return fig

@app.callback(Output('graph4','figure'),
                [Input('demo-dropdown-2','value')])
def update_figure(input1):
    results = get_graph_cats(df,input1)
    trace2 = go.Bar(x = results['yearmonth'], y = results['actual_amount'],
                    name = 'Category Sales')
    fig1 = go.Figure(data = [trace2], layout = {
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['background'],
        'font': {
            'color': colors['text']
        }})
    return fig1

if __name__ == '__main__':
    app.run_server(debug=True)

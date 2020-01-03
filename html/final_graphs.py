from flask import Flask, render_template, request, url_for
import pandas as pd
import bokeh
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral5
from bokeh.models.tools import HoverTool
from bokeh.layouts import gridplot
from bokeh.models.widgets import Panel, Tabs
from bokeh.embed import components

app = Flask(__name__)

def create_chart(df):
    categories = sorted(df['category'].unique().tolist())
    grouped = df.groupby('category').sum()
    source = ColumnDataSource(grouped)
    cats = source.data['category'].tolist()
    p = figure(x_range=cats, plot_width = 800)
    p.sizing_mode = 'scale_width'
    p.sizing_mode = 'scale_height'
    color_map = factor_cmap(field_name = 'category',palette = Spectral5, factors=cats)
    p.vbar(x='category',top='actual_amount',source=source,width=0.70,color=color_map)
    p.title.text = 'Spend by category'
    p.xaxis.axis_label = 'Category'
    p.yaxis.axis_label = 'Actual amounts'
    p.xaxis.major_label_orientation = 'vertical'

    hover = HoverTool()
    hover.tooltips = [("Totals","@actual_amount")]
    hover.mode = 'vline'
    p.add_tools(hover)
    return p

def create_chart_2(df):
    categories = sorted(df['acct_type'].unique().tolist())
    grouped = df.groupby('acct_type').sum()
    source = ColumnDataSource(grouped)
    cats = source.data['acct_type'].tolist()
    p = figure(x_range=cats, plot_width = 800)
    p.sizing_mode = 'scale_width'
    p.sizing_mode = 'scale_height'
    color_map = factor_cmap(field_name = 'acct_type',palette = Spectral5, factors=cats)
    p.vbar(x='acct_type',top='actual_amount',source=source,width=0.70,color=color_map)
    p.title.text = 'Spend by Account'
    p.xaxis.axis_label = 'Account'
    p.yaxis.axis_label = 'Actual amounts'
    p.xaxis.major_label_orientation = 'vertical'

    hover = HoverTool()
    hover.tooltips = [("Totals","@actual_amount")]
    hover.mode = 'vline'
    p.add_tools(hover)
    return p

def append_dict(categories,df,yrmonth):
    ym = df[df['YearMonth'] == yrmonth].groupby('category')['actual_amount'].sum()
    for i in categories:
        if i.lower() not in ym.index:
            ym.loc[i] = 0.0

    ym = ym.sort_index()
    ym_values = ym.values.tolist()
    return ym_values

def budget_chart(categories,df,yrmonth):
    ym = df[df['YearMonth']== yrmonth].groupby('category')['actual_amount'].sum()
    for i in categories:
        if i.lower() not in ym.index:
            ym.loc[i] = 0.0

    ym = ym.sort_index()
    ym_values = ym.values.tolist()
    return ym_values

def budgetvalues(categories,df):
    budget_dict = {}
    budgets = {'car fuel' : 100, 'food' : 200, 'personal' : 250, 'shopping' : 50}
    for i in categories:
        budget_dict[i] = 0

    for i in budget_dict:
        for j in budgets:
            if i == j:
                budget_dict.update({i:budgets[j]})
    budget_list = []
    for i in budget_dict:
        budget_list.append(budget_dict[i])
    return budget_list

def budget_graph(categories,df):
    new_labels = ['Budget','Actuals']
    new_dict = {'labels':categories}
    labels = ['Budget']
    for i in labels:
        new_dict[i] = []
        new_dict.update({i:budgetvalues(categories,df)})

    labels = ['Actuals']
    for i in labels:
        new_dict[i] = []
        new_dict.update({i:budget_chart(categories,df,'20197')})

    x = [ (category, label1) for category in categories for label1 in new_labels]
    counts = sum(zip(new_dict['Budget'],new_dict['Actuals']),())

    source = ColumnDataSource(data = dict(x=x, counts=counts))

    p=figure(x_range = FactorRange(*x),plot_height = 600, plot_width = 800, title = "Cat spend by yearmonth", toolbar_location = None, tools = "hover", tooltips = "@x : @$name")
    p.vbar(x='x', top = 'counts', width = 0.9, source=source, line_color = "white", fill_color = factor_cmap('x',palette = Spectral5, factors = new_labels, start=1, end=2), name = "counts")

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xaxis.group_label_orientation = 'vertical'
    p.xgrid.grid_line_color = None
    # p.sizing_mode = 'scale_width'
    # show(p)
    return p

def cat_date_chart(categories,df):
    new_dict = {'cats':categories}
    dates = ['20197','20198']
    for i in dates:
        new_dict[i] = []
        new_dict.update({i:append_dict(categories,df,i)})

    x = [ (category, yearmonth) for category in categories for yearmonth in dates]
    counts = sum(zip(new_dict['20197'],new_dict['20198']),())
    source = ColumnDataSource(data = dict(x=x, counts=counts))

    p=figure(x_range = FactorRange(*x), plot_height = 550, plot_width = 800, title = "Amounts by categories", toolbar_location = None, tools = "hover", tooltips = "@x sum: @$name")
    p.vbar(x='x', top = 'counts', width = 0.9, source=source, name = "counts")

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xaxis.group_label_orientation = 'vertical'
    p.xgrid.grid_line_color = None
    # p.sizing_mode = 'scale_width'

    return p

def line_chart(df):
    date_label = ['20197','20198']
    cat_sum = df.groupby('YearMonth').sum().sort_index()
    food_sum = df[df['category'] == 'food'].groupby('YearMonth').sum().sort_index()
    cat_list = cat_sum.values.tolist()
    food_list =food_sum.values.tolist()

    source = ColumnDataSource(cat_sum)
    source1 = ColumnDataSource(food_sum)

    p = figure(x_range = date_label,plot_width = 800)
    p.line(x='YearMonth', y='actual_amount',line_width=3,source=source, color = Spectral5[1], legend = 'Total Spend')
    p.line(x='YearMonth', y='actual_amount',line_width=3, source=source1, color = Spectral5[0], legend = 'Total Food Spend')
    p.title.text = 'Spending Trends'
    p.yaxis.axis_label = 'Total Amounts'

    return p

@app.route("/index",methods = ['POST','GET'])
def index():
    df = pd.read_csv('bokeh_test.csv')
    df['tran_date'] = pd.to_datetime(df.tran_date,format = '%m/%d/%Y')
    df['Year'] = pd.DatetimeIndex(df['tran_date']).year
    df['Month'] = pd.DatetimeIndex(df['tran_date']).month
    df['YearMonth'] = df['Year'].map(str)+df['Month'].map(str)
    df['category'] = df['category'].str.lower()

    dates = ['20197','20198']
    current_date = request.args.get('select_date')
    if current_date == None:
        current_date = dates[0]
    df_chart = df[df['YearMonth'] == current_date]
    plot = create_chart(df_chart)
    plot2 = create_chart_2(df_chart)

    by_category = Panel(child=plot, title="By Category")
    by_account = Panel(child=plot2, title="By Account")
    tabs = Tabs(tabs=[by_category, by_account])
    script, div = components(tabs)

    categories = sorted(df['category'].unique().tolist())
    yearmonths = sorted(df['YearMonth'].unique().tolist())

    new_dict = {'categories' : categories}

    # grid = gridplot([[cat_date_chart(categories,df),budget_graph(categories,df)]])

    # script1, div1 = components(grid)

    script2, div2 = components(line_chart(df))

    script3,div3 = components(cat_date_chart(categories,df))
    script4,div4 = components(budget_graph(categories,df))
    return render_template("index.html", script=script,div=div,script2 = script2, div2 = div2, script3  = script3, div3 = div3, script4 = script4, div4=div4, dates=dates,current_date=current_date)

if __name__ == '__main__':
	app.run(port=5000, debug=True)

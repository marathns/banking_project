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

def create_chart(df):
    categories = sorted(df['category'].unique().tolist())
    grouped = df.groupby('category').sum()
    source = ColumnDataSource(grouped)
    cats = source.data['category'].tolist()
    p = figure(x_range=cats, plot_width = 500)
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
    p = figure(x_range=cats, plot_width = 500)

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

def line_chart(df,dates,inp_cat):
    date_label = dates
    sum_all_categories = df.groupby('YearMonth').sum().sort_index()
    sum_category = df[df['category'] == inp_cat].groupby('YearMonth').sum().sort_index()

    # food_sum = df[df['category'] == 'food'].groupby('YearMonth').sum().sort_index()

    all_categories_list = sum_all_categories.values.tolist()
    category_list =sum_category.values.tolist()

    source = ColumnDataSource(sum_all_categories)
    source1 = ColumnDataSource(sum_category)

    p = figure(x_range = date_label,  plot_width = 500, plot_height = 550)
    p.line(x='YearMonth', y='actual_amount',line_width=3,source=source, color = Spectral5[1], legend = 'Total Spend')
    p.line(x='YearMonth', y='actual_amount',line_width=3, source=source1, color = Spectral5[0], legend = 'Total {} Spend'.format(inp_cat))
    p.title.text = 'Spending Trends'
    p.yaxis.axis_label = 'Total Amounts'

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

def budget_graph(categories,df,current_date):
    new_labels = ['Budget','Actuals']
    new_dict = {'labels':categories}
    labels = ['Budget']
    for i in labels:
        new_dict[i] = []
        new_dict.update({i:budgetvalues(categories,df)})

    labels = ['Actuals']
    for i in labels:
        new_dict[i] = []
        new_dict.update({i:budget_chart(categories,df,current_date)})

    x = [ (category, label1) for category in categories for label1 in new_labels]
    counts = sum(zip(new_dict['Budget'],new_dict['Actuals']),())

    source = ColumnDataSource(data = dict(x=x, counts=counts))

    p=figure(x_range = FactorRange(*x),plot_height = 600, plot_width = 700, title = "Budgets vs Actuals", toolbar_location = None, tools = "hover", tooltips = "@x : @$name")
    p.vbar(x='x', top = 'counts', width = 0.9, source=source, line_color = "white", fill_color = factor_cmap('x',palette = Spectral5, factors = new_labels, start=1, end=2), name = "counts")

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xaxis.group_label_orientation = 'vertical'
    p.xgrid.grid_line_color = None
    # p.sizing_mode = 'scale_width'
    # show(p)
    return p

def cat_date_chart(categories,df,dates):
    new_dict = {'cats':categories}
    dates = dates
    for i in dates:
        new_dict[i] = []
        new_dict.update({i:append_dict(categories,df,i)})

    x = [ (category, yearmonth) for category in categories for yearmonth in dates]
    counts = sum(zip(new_dict['20191'],new_dict['20192']),())
    source = ColumnDataSource(data = dict(x=x, counts=counts))
    # print(new_dict)
    p=figure(x_range = FactorRange(*x), plot_height = 550, plot_width = 800, title = "Amounts by categories", toolbar_location = None, tools = "hover", tooltips = "@x sum: @$name")
    p.vbar(x='x', top = 'counts', width = 0.9, source=source, name = "counts")

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xaxis.group_label_orientation = 'vertical'
    p.xgrid.grid_line_color = None
    # p.sizing_mode = 'scale_width'

    return p

def date_cat_chart(df,categories,dates,cat):

    x = []

    amnts = []
    for i in dates:
        ym = df[df['YearMonth'] == i].groupby('category',as_index=False)['actual_amount'].sum()
        val = ym[ym['category'] == cat].actual_amount
        if len(val) == 0:
            amnts.append(0)
        else:
            amnts.append(max(val))
        x.append((cat,i))
    # print(x)
    counts = tuple(amnts)
    source = ColumnDataSource(data = dict(x=x, counts=counts))

    p=figure(x_range = FactorRange(*x), plot_height = 550, plot_width = 500, title = "Monthly spend / category", toolbar_location = None, tools = "hover", tooltips = "@x sum: @$name")
    p.vbar(x='x', top = 'counts', width = 0.9, source=source, name = "counts")

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xaxis.group_label_orientation = 'vertical'
    p.xgrid.grid_line_color = None
    return p


def budgeting_graph(df,current_date,conn):
    cur = conn.cursor()
    sel_date = current_date
    cur.execute("select * from budgeting where period = '{}'".format(sel_date))
    results = cur.fetchall()

    df_selected = df[df['YearMonth'] == sel_date]
    period_cats = sorted(df_selected['category'].unique().tolist())

    budget_categories = []
    for i in period_cats:
        index = 0
        for j in results:
            if i == j[2]:
                budget_categories.append(j[3])
                index += 1
        if index < 1:
            budget_categories.append(0)
        else:
            pass

    ym = df_selected.groupby('category', as_index=False)['actual_amount'].sum()
    df_aa = ym['actual_amount'].tolist()

    new_dict = {}
    new_dict['Budget'] = budget_categories
    new_dict['Actual'] = df_aa
    new_labels = ['Budget','Actuals']
    counts = sum(zip(new_dict['Budget'],new_dict['Actual']),())

    x = [ (category, label1) for category in period_cats for label1 in new_labels]

    source = ColumnDataSource(data = dict(x=x, counts=counts))

    p=figure(x_range = FactorRange(*x),plot_height = 600, plot_width = 700, title = "Budgets vs Actuals", toolbar_location = None, tools = "hover", tooltips = "@x : @$name")
    p.vbar(x='x', top = 'counts', width = 0.9, source=source, line_color = "white", fill_color = factor_cmap('x',palette = Spectral5, factors = new_labels, start=1, end=2), name = "counts")

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xaxis.group_label_orientation = 'vertical'
    p.xgrid.grid_line_color = None

    return p

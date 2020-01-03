import uuid
import os,sys,inspect
import sqlite3
import pandas as pd
import config as Config
from os import environ
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify,session
from bokeh.layouts import gridplot
from bokeh.models.widgets import Panel, Tabs
from bokeh.embed import components
from splitwise import Splitwise

app = Flask(__name__)
app.secret_key = "flash message"

@app.route("/", methods = ['GET','POST'])

def home():
	from queries import sql_query,sql_edit_insert
	results = sql_query(''' SELECT * FROM transactions order by tran_date''')
	min = sql_query('select min(tran_date) from transactions')
	max = sql_query('select max(tran_date) from transactions')
	min = min[0][0]
	max = max[0][0]

	cats = sql_query(''' SELECT DISTINCT CATEGORY as Category FROM transactions	''')

	date_from = request.args.get('Date_From')
	date_to = request.args.get('Date_To')
	account = request.args.get('Account')
	accounts = ['All','DISCOVER','AMEX','CHASE','PNC','SPLITWISE']

	if account == None:
		account = 'All'
	if account == 'All':
		results = sql_query("select * from transactions where tran_date between '{}' and '{}' order by tran_date".format(date_from,date_to))
	else:
		results = sql_query("select * from transactions where tran_date between '{}' and '{}' and acct_type IN ('{}') order by tran_date".format(date_from,date_to,account))

	if request.method == 'POST':
		id_data = request.form['id']
		Actual_Amount = request.form['Actual_Amount']
		Account = request.form['Account']
		Category = request.form['Category']

		sql_edit_insert('Update transactions set actual_amount = ?, acct_type = ?, category = ? where transaction_id = ?', (Actual_Amount,Account,Category,id_data))
		flash("Data Updated Successfully")

	return render_template('home.html', results = results, min=min, max=max, cats = cats, date_from = date_from, date_to = date_to, acc=accounts, account=account)

@app.route("/update",methods=['POST'])
def update():
	from queries import sql_edit_insert, sql_query
	if request.method == 'POST':
		tran_id = request.form.get('tran_id')
		category = request.form.get('category')
		actual_amount = request.form.get('actual_amount')
		sql_edit_insert('Update transactions set actual_amount = ?, category = ? where transaction_id = ?', (actual_amount,category,tran_id))
		return jsonify({'result':'success'})


@app.route('/insert',methods = ['POST','GET'])
def insert():
	from queries import sql_edit_insert,sql_insert,sql_query
	id4 = uuid.uuid4()
	cats = sql_query(''' SELECT DISTINCT CATEGORY as Category FROM transactions	''')
	if request.method == 'POST':
		tran_date = request.form['Insert_Date']
		tran_particulars = request.form['Insert_Particulars']
		amount = request.form['Insert_Amount']
		actual_amount = request.form['Insert_Actual_Amount']
		acct_type = request.form['Insert_Account_Type']
		category = request.form['Insert_Category']

		sql_insert('''insert into transactions
							(transaction_id,tran_date,tran_particulars,amount,actual_amount,acct_type,category)
							values ("{}","{}","{}","{}","{}","{}","{}")'''.format(id4,tran_date,tran_particulars,amount,actual_amount,acct_type,category))
	return render_template('insert.html',cats=cats)

@app.route('/get_trans',methods = ['POST','GET'])
def get_trans():

	import get_transactions as gt
	import json_to_text as jt
	import ml_test_exp as ml
	import file_to_db as fdb

	curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
	parent_dir = os.path.dirname(curr_dir)
	file_dir = os.path.join(parent_dir,'txt_files')
	file_name = os.path.join(file_dir,'trans_file.txt')

	if request.method == 'POST':
		get_date_from = request.form['Get_Trans_Date_From']
		get_date_to = request.form['Get_Trans_Date_To']
		if get_date_to < get_date_from:
			flash('From date should be before than to date')
		else:
			gt.get_source_transactions(get_date_from,get_date_to)
			jt.json_text()
			ml.text_ml(file_name)
			status = fdb.file_db(file_name)
			flash(status)
			if status != 'Data already present in the database':
				flash("Transactions from {} to {} added to DB".format(get_date_from,get_date_to))
			else:
				pass

	return render_template('get_trans.html')

@app.route('/ml_trans', methods = ['POST'])
def ml_trans():
	import hash_db as adb
	if request.method == 'POST':
		result = adb.after_db()
		flash(result)
		return redirect(url_for('home'))

@app.route('/budgeting', methods = ['POST','GET'])
def budgeting():
	curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
	parent_dir = os.path.dirname(curr_dir)
	db_path = os.path.join(parent_dir,'test.db')
	conn = sqlite3.connect(db_path)
	df = pd.read_sql_query('select * from transactions',conn)
	df = df[df['category'] != 'payment']
	df['YearMonth'] = pd.DatetimeIndex(df['tran_date']).year.map(str)+pd.DatetimeIndex(df['tran_date']).month.map(str)
	df['category'] = df['category'].str.lower()

	all_categories = sorted(df['category'].unique().tolist())
	dates = df['YearMonth'].unique().tolist()
	curr_date = str(pd.datetime.now().year) + str((pd.datetime.now().month)-1)
	max_date = str(int(max(dates)) + 1)

	dates.append(max_date)
	dates = sorted(dates)

	current_date = request.args.get('get_date')
	if current_date == None:
		current_date = dates[0]

	df_budget = pd.read_sql_query("select * from budgeting where period = '{}'".format(current_date),conn)

	df_budget_list = df_budget['category'].tolist()

	df_cat = df[df['YearMonth'] == current_date]

	select_cats = []
	sel_categories = sorted(df_cat['category'].unique().tolist())

	for i in sel_categories:
		if i in df_budget_list:
			select_cats.append([i,max(df_budget[df_budget['category'] == i].amount)])
		else:
			select_cats.append([i,0])

	all_cats = []
	for i in all_categories:
		all_cats.append([i,0])
	if current_date >= max_date:
		categories = all_cats
	else:
		categories = select_cats

	return render_template('budgeting.html', dates = dates, current_date=current_date, categories=categories)

@app.route('/budget_update',methods = ['POST'])
def budget_update():
	curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
	parent_dir = os.path.dirname(curr_dir)
	db_path = os.path.join(parent_dir,'test.db')
	conn = sqlite3.connect(db_path)
	cur = conn.cursor()
	if request.method == 'POST':
		btn_id = request.form.get('btn_id')
		curr_date = request.form.get('curr_date')
		value = request.form.get('category')
		print(btn_id,curr_date,value)
		cur.execute('select distinct budget_key from budgeting')
		budget_key_list = []
		results = cur.fetchall()
		for i in results:
		    budget_key_list.append(i[0])
		if curr_date+btn_id not in budget_key_list:
		    cur.execute(''' insert into budgeting values ('{}','{}','{}','{}')'''.format(curr_date+btn_id,curr_date,btn_id,value))
		    conn.commit()
		else:
		    cur.execute(''' update budgeting
		                    set amount = '{}'
		                    where budget_key = '{}'
		                    '''.format(value, curr_date+btn_id))
		    conn.commit()
		return jsonify({'result':'success'})

@app.route('/dashboard',methods = ['POST','GET'])
def dashboard():
	from queries import sql_query
	from dashboard import create_chart, create_chart_2, line_chart,cat_date_chart,budget_graph,date_cat_chart,budgeting_graph
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

	df['YearMonth'] = pd.DatetimeIndex(df['tran_date']).year.map(str)+pd.DatetimeIndex(df['tran_date']).month.map(str)
	df['category'] = df['category'].str.lower()

	dates = df['YearMonth'].unique().tolist()

	current_date = request.args.get('select_date')
	if current_date == None:
		current_date = dates[0]

	df_chart = df[df['YearMonth'] == current_date]

	plot = create_chart(df_chart)
	plot2 = create_chart_2(df_chart)

	by_category = Panel(child=plot, title="By Category")
	by_account = Panel(child=plot2, title="By Account")
	tabs = Tabs(tabs=[by_category, by_account])

	categories = sorted(df['category'].unique().tolist())

	yearmonths = sorted(df['YearMonth'].unique().tolist())

	curr_cat = request.args.get('select_cat')
	if curr_cat == None:
		curr_cat = categories[0]

	script, div = components(tabs)
	script2, div2 = components(line_chart(df,dates,curr_cat))
	script3,div3 = components(date_cat_chart(df,categories,dates,curr_cat))
	script4, div4 = components(budgeting_graph(df,current_date, conn))

	return render_template("dashboard.html", script=script,div=div, script2 = script2, div2 = div2, script3  = script3, div3 = div3,
	script4 = script4, div4=div4, dates=dates,current_date=current_date,categories=categories,curr_cat=curr_cat)



@app.route("/splitwise", methods = ['POST','GET'])
def splitwise():
	if 'access_token' in session:
        # return redirect(url_for("home2.html"))
		return render_template("home2.html")
	return render_template("home2.html")

@app.route("/login",methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        get_date_from = request.form['Get_Trans_Date_From']
        get_date_to = request.form['Get_Trans_Date_To']
        session['date_from'] = get_date_from
        session['date_to'] = get_date_to
    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    url, secret = sObj.getAuthorizeURL()
    session['secret'] = secret
    return redirect(url)


@app.route("/authorize")
def authorize():

    if 'secret' not in session:
        return redirect(url_for("login"))

    oauth_token    = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    access_token = sObj.getAccessToken(oauth_token,session['secret'],oauth_verifier)
    session['access_token'] = access_token

    return redirect(url_for("expenses"))

@app.route("/expenses")
def expenses():
	import ml_test_exp as ml
	import file_to_db as fdb
	if 'access_token' not in session:
		return redirect(url_for("home2"))

	curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
	parent_dir = os.path.dirname(curr_dir)
	file_dir = os.path.join(parent_dir,'txt_files')
	file_name = os.path.join(file_dir,'trans_splitwise.txt')

	sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
	sObj.setAccessToken(session['access_token'])

	exps = sObj.getExpenses(dated_after = session['date_from'], dated_before = session['date_to'], limit = 0)
	expenseids = []
	for i in exps:
		expenseids.append(i.getId())

	exp_concat = []
	for i in expenseids:
		exp = sObj.getExpense(i)
		for j in exp.getUsers():
			if j.getFirstName() == 'Marathe':#3708390:

				if exp.getCreatedBy().getFirstName() == j.getFirstName() or exp.getDescription() == 'Payment':
					owed = 0
				else:
					owed = j.getOwedShare()
				exp_concat.append([exp.getId(),exp.getDate(),'',j.getFirstName(),exp.getCost(),exp.getCategory().getName(),exp.getDescription(),'SPLITWISE','', owed])
			else:
				pass


	df = pd.DataFrame(exp_concat, columns = ['transation_id','date','account_id','account_owner','amount','old_category','name','acct_type','pending','actual_amount'])
	df['category'] = ''
	df['date'] = pd.to_datetime(df['date']).dt.date
	df = df[df['name'] != 'Settle all balances']
	df.to_csv(os.path.join(file_dir,'trans_splitwise.txt'),sep='|',header=False,index=False)
	ml.text_ml(file_name)
	status = fdb.file_db(file_name)
	if status != 'Data already present in the database':
		flash("Transactions from {} to {} added to DB".format(session['date_from'],session['date_to']))
	else:
		flash(status)
	session.pop('secret')
	session.pop('date_from')
	session.pop('date_to')
	return render_template('close_split.html')


if __name__ == '__main__':
	app.run(debug=True)

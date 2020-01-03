from flask import Flask, render_template, redirect, session, url_for, request,jsonify,session
from splitwise import Splitwise
import config as Config
import os,sys,inspect
import pandas as pd

app = Flask(__name__)
app.secret_key = "test_secret_key"

@app.route("/splitwise", methods = ['POST','GET'])
def home():
    if 'access_token' in session:
        return redirect(url_for("login"))
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
        return redirect(url_for("home2"))

    oauth_token    = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    access_token = sObj.getAccessToken(oauth_token,session['secret'],oauth_verifier)
    session['access_token'] = access_token

    return redirect(url_for("expenses"))

@app.route("/expenses")
def expenses():
    if 'access_token' not in session:
        return redirect(url_for("home2"))

    curr_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    parent_dir = os.path.dirname(curr_dir)
    file_dir = os.path.join(parent_dir,'txt_files')

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
    
    session.clear()
    return render_template('close_split.html')
    # return render_template('expenses.html', exps = exp_concat)


if __name__ == "__main__":
    app.run(debug=True)

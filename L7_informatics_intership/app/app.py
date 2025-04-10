from datetime import datetime
import smtplib
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify, render_template, redirect, url_for


#here for the api response i have didn't do separte UI it will return in json format in browsers
app = Flask(__name__)
#Sql Query and ORM abstarction Implement
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense_tracker.db'   # here we are configuring the db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
#this will create a local db file under the instance under that expense_tracer.db , i was not using remote server here so this local db i will push into git
class Expense(db.Model): #here we are configuring the database model like type of the data we are storing and their sizes
    id = db.Column(db.Integer, primary_key=True)#here we are specifying what type of data it is and all 
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200))

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(7), nullable=False)
    alert_threshold = db.Column(db.Float, default=0.1)

def send_email_alert(subject, body, to_email):  #here we are using stmp becoz since it is like free and we have sendgrid and all but i am not using here becoz its a paid 
    sender =os.getenv('EMAIL_ID')
    password = os.getenv('EMAIL_PASSWORD')
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server: #initliazing the smpt , which will have a 587 which is mostly supported
            server.starttls()
            server.login(sender, password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender, to_email, message)
    except Exception as e:
        print("Failed to send email:", e)

# here it is a web routes which will render the page
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add-expense-form')
def add_expense_form():
    return render_template('addexpense.html')

@app.route('/set-budget-form')
def set_budget_form():
    return render_template('setbudget.html')

@app.route('/report-form')
def report_form():
    categories = db.session.query(Expense.category).distinct().all() # here we are accessing the category from database for drop down in html so that they can easily choose it
    categories = [c[0] for c in categories]
    return render_template('report.html', categories=categories)
    

#this the route for the the add expense api which wil add the expense
@app.route('/add-expense', methods=['POST'])
def add_expense():
    category = request.form['category']# this will take the values from the from and intialize to the variable for the fruther processing
    amount = float(request.form['amount'])
    date = datetime.strptime(request.form['date'], "%Y-%m-%d").date()     #converting date in the desired form
    description = request.form.get('description', '')

    expense = Expense(category=category, amount=amount, date=date, description=description)
    db.session.add(expense)
    db.session.commit()  #to maintain the state of you expense_tracker we are commiting the things

    month_str = date.strftime("%Y-%m")
    bdget = Budget.query.filter_by(category=category, month=month_str).first()  #from orm we are filtering the details by category and month 
    if bdget:
        total_spent = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.category == category,                           #filtering the data based on the month and year and finding the total spent amount 
            db.extract('month', Expense.date) == date.month,
            db.extract('year', Expense.date) == date.year
        ).scalar() or 0

        if total_spent > bdget.amount:
            send_email_alert( # if the expensive is more than budge it will send the alerts
                "Your Budget has Exceeded ...........",
                f"You have exceeded the budget for {category} in {month_str}.",
                os.getenv('Receipent_Mail')   #u can specify the receipent email in .env file
            )
        elif (bdget.amount - total_spent) < (bdget.amount * bdget.alert_threshold):
            send_email_alert(   # it will send the alert for the users
                "............ Budget alert ...........",
                f"You have Only {bdget.amount - total_spent:.2f} left in your {category} budget for {month_str} month.",
                os.getenv('Receipent_Mail')  
            )

    return redirect(url_for('home'))

#this api is for setting up the budget
@app.route('/set-budget', methods=['POST'])         #this is the post api which takes the value html form
def set_budget():
    month = request.form['month']
    category = request.form['category']      #fetching the details from the form here
    amount = float(request.form['amount'])
    alert_threshold = float(request.form.get('alert_threshold', 0.1))  # getting the alert threshold u want to set 

    existing = Budget.query.filter_by(category=category, month=month).first()   #filtering data based on category and month
    if existing:  #if any data exits
        existing.amount = amount
        existing.alert_threshold = alert_threshold
    else:
        budget = Budget(category=category, amount=amount, month=month, alert_threshold=alert_threshold)  #intializing the Budget Model and adding it , if it is not already existing in db
        db.session.add(budget)
    db.session.commit() #commiting the session
    return redirect(url_for('home'))  #url which redirect back to home

#this api will return the monthly reprt 
@app.route('/report/monthly', methods=['GET'])
def report_monthly():
    year = int(request.args.get('year'))   #getting the data from html forms
    month = int(request.args.get('month'))
    total = db.session.query(db.func.sum(Expense.amount)).filter(
        db.extract('month', Expense.date) == month,    #summing the total amount by filetering data based on month and year
        db.extract('year', Expense.date) == year
    ).scalar() or 0   #if nothing there then it will be scalar()
    return jsonify({"year": year, "month": month, "total_spending": total})  #returning the json response

#this api will give the report based on catgory
@app.route('/report/category', methods=['GET'])
def report_category():
    month_str = request.args.get('month')#getting the data from html forms
    category = request.args.get('category')
    year, month = map(int, month_str.split('-'))

    spent = db.session.query(db.func.sum(Expense.amount)).filter(
        Expense.category == category,#summing the total amount by filetering data based on month and year
        db.extract('month', Expense.date) == month,
        db.extract('year', Expense.date) == year
    ).scalar() or 0

    budget = Budget.query.filter_by(category=category, month=month_str).first()  #then from that we are again filtering based on the category
    budgetamt = budget.amount if budget else 0

    return jsonify({
        "category": category,
        "spent": spent,
        "month": month_str,
     
        "budget": budgetamt,
        "remaining": budgetamt - spent
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

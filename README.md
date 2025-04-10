# L7_Informatics_Track_Expense
The Expense Tracker App lets users set category budgets, track daily spending, and get email alerts when limits are hit. It generates monthly and category-wise reports. Built with Flask and SQLAlchemy, and using SQLite for local development.
# Steps to be followed to run the project
Step 1: Clone the project from the git hub link specified in readme file

Step 2: IN .env file can specify the sender and receiver mail id which is kept blank now (Used for alerts)

Step 3: Install the required libraries under requirements.txt file use command pip install -r requirements.txt

Step 4: Local Db is configured by SQLALCHEMY_database, we can use it for data processing 

Step 5: Run the app.py file under the app folder

# TOOLS USED:
VS CODE,
Technology used:
flask app,
Sqlalchemy Database (for local DB),
HTML,CSS,
SMTP for Email sending

# Description:
Users may create monthly and category-specific spending reports, set budgets for various categories, and keep tabs on their daily spending with the Expense Tracker App. Additionally, when the budget is surpassed or a specific threshold is reached, the program sends out email alerts. For local development, the application uses SQLite to store data, and Flask and SQLAlchemy are used to handle database interactions and backend functionality.

Qualities
Essential Elements
Users have the option to record their daily expenses, including the category, amount, date, and description.

Establish Monthly Budgets: Each category (such as "Food" and "Transport") may have a monthly budget specified by the user.

Alerts for Exceeded Budgets: An email alert is issued whenever a user's expenditures surpass the allocated budget for a certain category.

Monthly Spending Report: This allows users to see how much was spent in a given month.

Category-wise Spending Report: Users can examine monthly spending for any specific category.


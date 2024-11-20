"""Main"""
from flask import Flask, render_template, request, redirect, url_for, session
import os
from dotenv import load_dotenv
from user_auth import UserAuth
from bank_system import BankSystem
from sqlalchemy.orm import sessionmaker
from database.init_db import engine
from database import User, Account, Transaction


app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../banking_app/templates')), static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../banking_app/static')))
load_dotenv(dotenv_path=".env")
app.secret_key = os.getenv("SECRET_KEY")

# Set up the database session
Session = sessionmaker(bind=engine)
db_session = Session()


# Initialize banking system and user authentication
bank_system = BankSystem()
user_auth = UserAuth(bank_system)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check credentials against the database
    user = db_session.query(User).filter_by(username=username).first()
    if user and user.password_hash == password:
        session['user_id'] = username
        return redirect(url_for('dashboard'))
    else:
        return "Invalid username or password", 401

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Fetch user accounts from the database
    user = db_session.query(User).filter_by(username=session['user_id']).first()
    if user:
        user_accounts = db_session.query(Account).filter_by(user_id=user.user_id).all()
    else:
        user_accounts = []
    return render_template('dashboard.html', accounts=user_accounts)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        from_account_id = int(request.form.get('fromAccount'))
        to_account = request.form.get('toAccount')
        amount = float(request.form.get('amount'))
        notes = request.form.get('notes')
        frequency = request.form.get('frequency')

        # Log transfer details (this will eventually be replaced with database logic)
        print(f"Transfer from Account ID: {from_account_id}")
        print(f"To Account: {to_account}")
        print(f"Amount: {amount}")
        print(f"Notes: {notes}")
        print(f"Frequency: {frequency}")

        return "Transfer processed successfully!"

    # Fetch user accounts from the database
    user = session.query(User).filter_by(username=session['user_id']).first()
    if user:
        user_accounts = session.query(Account).filter_by(user_id=user.user_id).all()
    else:
        user_accounts = []
    return render_template('transfer.html', accounts=user_accounts)

@app.route('/history')
def transaction_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    filter_type = request.args.get("type")
    # Filter logic can be added here once the database is implemented
    if filter_type == "debit":
        return "Filtered for Expenses (Debit)"
    elif filter_type == "credit":
        return "Filtered for Income (Credit)"
    elif filter_type == "transfer":
        return "Filtered for Transfers"
    else:
        return render_template('history.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result = user_auth.register_user(username, password)
        if result['success']:
            return redirect(url_for('login'))
        return render_template('register.html', error=result['message'])
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
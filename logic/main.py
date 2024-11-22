"""Main"""
from flask import Flask, render_template, request, redirect, url_for, session
import os
import bcrypt
from dotenv import load_dotenv
from user_auth import UserAuth
from bank_system import BankSystem
from database.init_db import engine
from database.models import User, Account, Transaction
from sqlalchemy.orm import sessionmaker


app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../banking_app/templates')), static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../banking_app/static')))
load_dotenv(dotenv_path=".env")
app.secret_key = os.getenv("SECRET_KEY")

# Set up the database session
Session = sessionmaker(bind=engine)
db_session = Session()


# Initialize banking system and user authentication
bank_system = BankSystem()
user_auth = UserAuth(bank_system, db_session)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check credentials against the database
    user = db_session.query(User).filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        session['user_id'] = str(user.user_id)  # Store user_id (UUID) as string
        return redirect(url_for('dashboard'))
    else:
        return "Invalid username or password", 401

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Fetch user accounts from the database
    user = db_session.query(User).filter_by(user_id=session['user_id']).first()
    if user:
        user_accounts = db_session.query(Account).filter_by(user_id=user.user_id).all()
        total_balance = sum(account.balance for account in user_accounts)
        user_name = user.username
    else:
        user_accounts = []
        total_balance = 0.0
        user_name = "Guest"

    # Placeholder for transactions (keep as is)
    transactions = [
        {"date": "08/03/2024", "type": "expense", "description": "Marty S.A.S.", "amount": 852.04},
        {"date": "02/03/2024", "type": "expense", "description": "Groceries", "amount": 120.50},
        {"date": "01/03/2024", "type": "expense", "description": "Royer", "amount": 487.09},
        {"date": "11/03/2024", "type": "income", "description": "Salary", "amount": 707.95},
        {"date": "08/03/2024", "type": "income", "description": "Bonus", "amount": 1931.61},
        {"date": "07/03/2024", "type": "income", "description": "Refund", "amount": 640.10},
    ]

    pending_transfers = 3  # Placeholder for pending transfers

    return render_template(
        'dashboard.html',
        accounts=user_accounts,
        total_balance=total_balance,
        user_name=user_name,
        transactions=transactions,
        pending_transfers=pending_transfers
    )


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = db_session.query(User).filter_by(user_id=session['user_id']).first()
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        from_account_id = request.form.get('fromAccount')
        transfer_type = request.form.get('transferType')
        amount = float(request.form.get('amount'))

        # Retrieve the account details from the database
        from_account = db_session.query(Account).filter_by(account_id=from_account_id, user_id=user.user_id).first()

        if not from_account or from_account.balance < amount:
            return "Insufficient funds or invalid account.", 400

        if transfer_type == "internal":
            to_account_id = request.form.get('toInternalAccount')
            to_account = db_session.query(Account).filter_by(account_id=to_account_id, user_id=user.user_id).first()
            if not to_account:
                return "Invalid target account.", 400

            # Process internal transfer
            from_account.balance -= amount
            to_account.balance += amount
            db_session.commit()
            print(f"Internal Transfer: ${amount} from {from_account.account_id} to {to_account.account_id}")

        elif transfer_type == "external":
            to_account = request.form.get('toExternalAccount')
            notes = request.form.get('notesExternal')

            # Process external transfer
            from_account.balance -= amount
            db_session.commit()
            print(f"External Transfer: ${amount} from {from_account.account_id} to External Account {to_account}. Notes: {notes}")

        return redirect(url_for('dashboard'))

    # Fetch user accounts from the database
    user_accounts = db_session.query(Account).filter_by(user_id=user.user_id).all()
    return render_template('transfer.html', accounts=user_accounts)

@app.route('/history')
def transaction_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    filter_type = request.args.get("type")
    # Placeholder for filtered transactions
    transactions = [
        {"date": "08/03/2024", "type": filter_type or "all", "description": "Example Transaction", "amount": 500.0}
    ]
    
    return render_template('history.html', transactions=transactions)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']  # Collect email from the form
        password = request.form['password']
        result = user_auth.register_user(username, email, password)
        if result['success']:
            return redirect(url_for('login'))
        else:
            error_message = result.get('message', 'Registration failed.')
            return render_template('registration.html', error=error_message)
    return render_template('registration.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
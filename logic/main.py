"""main.py"""
from flask import Flask, render_template, request, redirect, url_for, session
import os
import bcrypt
from dotenv import load_dotenv
from user_auth import UserAuth
from bank_system import BankSystem
from database.init_db import engine
from database.models import User, Account, Transaction
from sqlalchemy.orm import sessionmaker
from functools import wraps
from abc import ABC, abstractmethod

class BankApp:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BankApp, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initialize the BankApp with Flask, database, and user authentication.
        This follows the Singleton pattern to ensure only one instance is created.
        """
        # Initialize the Flask app
        self._app = Flask(
            __name__,
            template_folder=os.path.abspath(
                os.path.join(os.path.dirname(__file__), '../banking_app/templates')
            ),
            static_folder=os.path.abspath(
                os.path.join(os.path.dirname(__file__), '../banking_app/static')
            )
        )
        load_dotenv(dotenv_path=".env")
        self._app.secret_key = os.getenv("SECRET_KEY")

        # Set up the database session
        Session = sessionmaker(bind=engine)
        self._db_session = Session()

        # Initialize banking system and user authentication
        self._bank_system = BankSystem()
        self._user_auth = UserAuth(self._bank_system, self._db_session)

        # Set up the routes
        self.setup_routes()

    @property
    def app(self):
        """
        Getter for the Flask app instance.
        """
        return self._app

    @property
    def db_session(self):
        """
        Getter for the database session.
        """
        return self._db_session

    @property
    def bank_system(self):
        """
        Getter for the bank system instance.
        """
        return self._bank_system

    @property
    def user_auth(self):
        """
        Getter for the user authentication instance.
        """
        return self._user_auth

    def setup_routes(self):
        @self._app.route('/')
        def login():
            return render_template('login.html')

        @self._app.route('/login', methods=['POST'])
        def handle_login():
            username = request.form.get('username')
            password = request.form.get('password')

            # Check credentials against the database
            user = self._db_session.query(User).filter_by(username=username).first()
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                session['user_id'] = str(user.user_id)  # Store user_id (UUID) as string
                return redirect(url_for('dashboard'))
            else:
                return "Invalid username or password", 401

        @self._app.route('/dashboard')
        @login_required
        def dashboard():
            # Fetch user accounts from the database
            user = self._db_session.query(User).filter_by(user_id=session['user_id']).first()
            if user:
                user_accounts = self._db_session.query(Account).filter_by(user_id=user.user_id).all()
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

        @self._app.route('/transfer', methods=['GET', 'POST'])
        @login_required
        def transfer():
            user = self._db_session.query(User).filter_by(user_id=session['user_id']).first()
            if not user:
                return redirect(url_for('login'))

            if request.method == 'POST':
                from_account_id = request.form.get('fromAccount')
                transfer_type = request.form.get('transferType')
                amount = float(request.form.get('amount'))

                # Retrieve the account details from the database
                from_account = self._db_session.query(Account).filter_by(account_id=from_account_id, user_id=user.user_id).first()

                if not from_account or from_account.balance < amount:
                    return "Insufficient funds or invalid account.", 400

                if transfer_type == "internal":
                    to_account_id = request.form.get('toInternalAccount')
                    to_account = self._db_session.query(Account).filter_by(account_id=to_account_id, user_id=user.user_id).first()
                    if not to_account:
                        return "Invalid target account.", 400

                    # Process internal transfer
                    from_account.balance -= amount
                    to_account.balance += amount
                    self._db_session.commit()
                    print(f"Internal Transfer: ${amount} from {from_account.account_id} to {to_account.account_id}")

                elif transfer_type == "external":
                    to_account = request.form.get('toExternalAccount')
                    notes = request.form.get('notesExternal')

                    # Process external transfer
                    from_account.balance -= amount
                    self._db_session.commit()
                    print(f"External Transfer: ${amount} from {from_account.account_id} to External Account {to_account}. Notes: {notes}")

                return redirect(url_for('dashboard'))

            # Fetch user accounts from the database
            user_accounts = self._db_session.query(Account).filter_by(user_id=user.user_id).all()
            return render_template('transfer.html', accounts=user_accounts)

        @self._app.route('/history')
        @login_required
        def transaction_history():
            filter_type = request.args.get("type")
            # Placeholder for filtered transactions
            transactions = [
                {"date": "08/03/2024", "type": filter_type or "all", "description": "Example Transaction", "amount": 500.0}
            ]

            return render_template('history.html', transactions=transactions)

        @self._app.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                username = request.form['username']
                email = request.form['email']  # Collect email from the form
                password = request.form['password']
                result = self._user_auth.register_user(username, email, password)
                if result['success']:
                    return redirect(url_for('login'))
                else:
                    error_message = result.get('message', 'Registration failed.')
                    return render_template('registration.html', error=error_message)
            return render_template('registration.html')

        @self._app.route('/logout')
        def logout():
            session.pop('user_id', None)
            return redirect(url_for('login'))

# Decorator for requiring login

def login_required(f):
    """
    Decorator to check if the user is logged in before accessing certain routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Command Pattern for Bank Operations

class Command(ABC):
    """
    Abstract base class representing a command that can be executed.
    """
    @abstractmethod
    def execute(self):
        pass

class DepositCommand(Command):
    def __init__(self, bank_system, user_id, account_id, amount):
        self._bank_system = bank_system
        self._user_id = user_id
        self._account_id = account_id
        self._amount = amount

    @property
    def amount(self):
        """Getter for the amount."""
        return self._amount

    @amount.setter
    def amount(self, value):
        """Setter for the amount."""
        self._amount = value

    def execute(self):
        """
        Execute the deposit operation.
        """
        self._bank_system.deposit(self._user_id, self._account_id, self._amount)

class WithdrawCommand(Command):
    def __init__(self, bank_system, user_id, account_id, amount):
        self._bank_system = bank_system
        self._user_id = user_id
        self._account_id = account_id
        self._amount = amount

    @property
    def amount(self):
        """Getter for the amount."""
        return self._amount

    @amount.setter
    def amount(self, value):
        """Setter for the amount."""
        self._amount = value

    def execute(self):
        """
        Execute the withdraw operation.
        """
        self._bank_system.withdraw(self._user_id, self._account_id, self._amount)

bank_app = BankApp()
app = bank_app.app  # to expose app to flaskCLI

if __name__ == "__main__":
    bank_app.run()
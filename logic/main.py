from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
import os
import bcrypt
from dotenv import load_dotenv
from logic.user_auth import UserAuth
from logic.bank_system import BankSystem
from database.init_db import engine
from database.models import User, Account, Transaction, Role
from database.models import TransactionType, TransactionStatus
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as ORM_Session
from functools import wraps
from abc import ABC, abstractmethod
import logging
from typing import Any, Callable, Union, Optional, Tuple, List, Dict

from werkzeug.wrappers import Response as WerkzeugResponse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class BankApp:
    _instance: Optional['BankApp'] = None

    def __new__(cls: type['BankApp'], *args: object, **kwargs: object) -> 'BankApp':
        if not cls._instance:
            cls._instance = super(BankApp, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the BankApp with Flask, database, and user authentication.
        This follows the Singleton pattern (only one instance is created)
        """
        self._app = Flask(
            __name__,
            template_folder=os.path.abspath(
                os.path.join(os.path.dirname(__file__),
                             '../banking_app/templates')
            ),
            static_folder=os.path.abspath(
                os.path.join(os.path.dirname(__file__),
                             '../banking_app/static')
            )
        )
        load_dotenv(dotenv_path=".env")
        self._app.secret_key = os.getenv("SECRET_KEY")
        Session = sessionmaker(bind=engine)
        self._db_session: ORM_Session = Session()
        self._bank_system = BankSystem()  # type: ignore
        self._user_auth = UserAuth(self._bank_system, self._db_session)  # type: ignore
        self.setup_routes()
        self.add_admin_user()

    @property
    def app(self) -> Flask:
        """
        Getter for the Flask app instance.
        """
        return self._app

    @property
    def db_session(self) -> ORM_Session:
        """
        Getter for the database session.
        """
        return self._db_session

    @property
    def bank_system(self) -> BankSystem:
        """
        Getter for the bank system instance.
        """
        return self._bank_system

    @property
    def user_auth(self) -> UserAuth:
        """
        Getter for the user authentication instance.
        """
        return self._user_auth

    def setup_routes(self) -> None:
        @self._app.route('/')
        def login() -> str:
            return render_template('login.html')

        @self._app.route('/login', methods=['POST'])
        def handle_login() -> WerkzeugResponse:
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            user: Optional[User] = self._db_session.query(User).filter_by(
                username=username.strip().lower()).first()
            if user and bcrypt.checkpw(password.encode('utf-8'),
                                       user.password_hash.encode('utf-8')):
                session['user_id'] = user.user_id
                if user.role == Role.admin:
                    return redirect(url_for('admin'))
                return redirect(url_for('dashboard'))
            else:
                return make_response("Invalid username or password", 401)

        @self._app.route('/dashboard')
        @login_required
        def dashboard() -> str:
            user_id = session.get('user_id')
            user: Optional[User] = self._db_session.query(User).filter_by(user_id=user_id).first()
            if user is not None:
                user_accounts: List[Account] = self._db_session.query(Account).filter_by(user_id=user.user_id).all()
                total_balance = sum(
                    account.balance for account in user_accounts)
                user_name = user.username

                recent_income = self._db_session.query(Transaction).join(Account).filter(
                    Account.user_id == user.user_id, Transaction.transaction_type.in_([TransactionType.deposit])
                ).order_by(Transaction.created_at.desc()).limit(5).all()

                recent_expenses = self._db_session.query(Transaction).join(Account).filter(
                    Account.user_id == user.user_id, Transaction.transaction_type.in_([TransactionType.withdrawal,
                                                                                       TransactionType.transfer])
                ).order_by(Transaction.created_at.desc()).limit(5).all()

                pending_transfers = self._db_session.query(Transaction).join(Account).filter(
                    Account.user_id == user.user_id, Transaction.status == TransactionStatus.pending
                ).count()
            else:
                user_accounts = []
                total_balance = 0.0
                user_name = "Guest"
                recent_income = []
                recent_expenses = []
                pending_transfers = 0

            return render_template(
                'dashboard.html',
                accounts=user_accounts,
                total_balance=total_balance,
                user_name=user_name,
                recent_income=recent_income,
                recent_expenses=recent_expenses,
                pending_transfers=pending_transfers
            )

        @self._app.route('/admin')
        @admin_required
        def admin() -> str:
            users = self._db_session.query(User).all()
            user_data = []
            for user in users:
                num_accounts = len(user.accounts)
                total_balance = sum(
                    account.balance for account in user.accounts)
                user_data.append({
                    'id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'num_accounts': num_accounts,
                    'balance': total_balance
                })
            return render_template('admin.html', users=user_data)

        @self._app.route('/admin/transaction', methods=['POST'])
        @admin_required
        def add_transaction() -> WerkzeugResponse:
            account_id = request.form.get('account_id', '0')
            amount_str = request.form.get('amount', '0')
            amount = float(amount_str)
            transaction_type = request.form.get('type', '')
            account: Optional[Account] = self._db_session.query(Account).filter_by(
                account_id=account_id).first()
            if not account:
                return make_response("Invalid account.", 400)

            if transaction_type == 'deposit':
                account.balance += amount
                transaction = Transaction(account_id=account_id,
                                          transaction_type=TransactionType.deposit,
                                          amount=amount, status=TransactionStatus.completed)
            elif transaction_type == 'withdraw':
                if account.balance < amount:
                    return make_response("Insufficient funds.", 400)
                account.balance -= amount
                transaction = Transaction(account_id=account_id,
                                          transaction_type=TransactionType.withdrawal,
                                          amount=amount,
                                          status=TransactionStatus.completed)
            else:
                return make_response("Invalid transaction type.", 400)

            self._db_session.add(transaction)
            self._db_session.commit()
            return redirect(url_for('admin'))

        @self._app.route('/transfer', methods=['GET', 'POST'])
        @login_required
        def transfer() -> Union[WerkzeugResponse, str]:
            user_id = session.get('user_id')
            user: Optional[User] = self._db_session.query(User).filter_by(
                user_id=user_id).first()
            if not user:
                return redirect(url_for('login'))

            if request.method == 'POST':
                try:
                    logger.debug(f"Received form data: {request.form}")

                    from_account_id_str = request.form.get('fromAccount', '0')
                    from_account_id = int(from_account_id_str)
                    transfer_type = request.form.get('transferType', '')
                    amount_str = request.form.get('amount', '0')
                    amount = float(amount_str)

                    from_account: Optional[Account] = self._db_session.query(Account).filter_by(
                        account_id=from_account_id, user_id=user.user_id
                    ).first()

                    if not from_account:
                        logger.error("Invalid source account.")
                        return make_response("Invalid source account.", 400)
                    if from_account.balance < amount:
                        logger.error("Insufficient funds.")
                        return make_response("Insufficient funds.", 400)

                    to_account: Optional[Account] = None

                    if transfer_type == "internal":
                        to_account_id_str = request.form.get('toInternalAccount', '0')
                        to_account_id = int(to_account_id_str)
                        to_account = self._db_session.query(Account).filter_by(
                            account_id=to_account_id, user_id=user.user_id
                        ).first()

                        if not to_account:
                            logger.error("Invalid target account.")
                            return make_response("Invalid target account.", 400)

                        logger.debug(f"Before Transfer - From Account Balance: {from_account.balance}, To Account Balance: {to_account.balance}")

                        from_account.balance -= amount
                        to_account.balance += amount

                        # Create transaction records
                        from_transaction = Transaction(
                            account_id=from_account_id,
                            transaction_type=TransactionType.withdrawal,
                            amount=amount,
                            status=TransactionStatus.completed
                        )
                        to_transaction = Transaction(
                            account_id=to_account_id,
                            transaction_type=TransactionType.deposit,
                            amount=amount,
                            status=TransactionStatus.completed
                        )

                        self._db_session.add_all(
                            [from_transaction, to_transaction])

                        logger.debug(f"After Transfer - From Account Balance: {from_account.balance}, To Account Balance: {to_account.balance}")

                        self._db_session.commit()
                        logger.info(f"Internal Transfer: ${amount} from {from_account.account_id} to {to_account.account_id}")

                    elif transfer_type == "external":
                        to_account_id_str = request.form.get('toExternalAccount', '0')
                        to_account_id = int(to_account_id_str)
                        to_account = self._db_session.query(Account).filter_by(
                            account_id=to_account_id).first()

                        if not to_account:
                            logger.error("Invalid external target account.")
                            return make_response("Invalid external target account.", 400)

                        # Process external
                        from_account.balance -= amount
                        to_account.balance += amount

                        # Create transaction records
                        from_transaction = Transaction(
                            account_id=from_account_id,
                            transaction_type=TransactionType.withdrawal,
                            amount=amount,
                            status=TransactionStatus.completed
                        )
                        to_transaction = Transaction(
                            account_id=to_account_id,
                            transaction_type=TransactionType.deposit,
                            amount=amount,
                            status=TransactionStatus.completed
                        )

                        self._db_session.add_all(
                            [from_transaction, to_transaction])

                        # Commit transaction
                        self._db_session.commit()
                        logger.info(f"External Transfer: ${amount} from {from_account.account_id} to {to_account.account_id}")

                    return redirect(url_for('dashboard'))

                except Exception as e:
                    self._db_session.rollback()
                    logger.exception("An error occurred during the transfer.")
                    return make_response(f"An error occurred during the transfer: {str(e)}", 500)

            # Fetch users
            user_accounts = self._db_session.query(Account).filter_by(
                user_id=user.user_id).all()
            return render_template('transfer.html', accounts=user_accounts)

        @self._app.route('/history')
        @login_required
        def transaction_history() -> str:
            return render_template('history.html')

        @self._app.route('/api/transactions', methods=['GET'])
        @login_required
        def api_transactions() -> WerkzeugResponse:
            user_id = session.get('user_id')
            transactions = self._db_session.query(Transaction).join(
                Account).filter(Account.user_id == user_id).order_by(
                    Transaction.created_at.desc()).all()

            transaction_list = [
                {
                    'date': transaction.account.created_at.strftime("%Y-%m-%d"),
                    'type': transaction.transaction_type.name,
                    'account': transaction.account.account_type,
                    'amount': transaction.amount,
                    'notes': ""
                }
                for transaction in transactions
            ]

            return jsonify(transaction_list)

        @self._app.route('/register', methods=['GET', 'POST'])
        def register() -> Union[WerkzeugResponse, str]:
            if request.method == 'POST':
                username = request.form['username'].strip().lower()
                email = request.form['email']
                password = request.form['password']
                result = self._user_auth.register_user(
                    username, email, password)  # type: ignore
                if result['success']:
                    # initial balances
                    new_user: Optional[User] = self._db_session.query(User).filter_by(
                        username=username).first()
                    if new_user is not None:
                        initial_accounts = [
                            Account(user_id=new_user.user_id,
                                    account_type='Checking Account',
                                    balance=500.00),
                            Account(user_id=new_user.user_id,
                                    account_type='Savings Account',
                                    balance=1500.00),
                            Account(user_id=new_user.user_id,
                                    account_type='Business Account',
                                    balance=3000.00)
                        ]
                        self._db_session.add_all(initial_accounts)
                        self._db_session.commit()

                        # initial transactions
                        for account in initial_accounts:
                            initial_transaction = Transaction(
                                account_id=account.account_id,
                                transaction_type=TransactionType.deposit,
                                amount=account.balance,
                                status=TransactionStatus.completed)
                            self._db_session.add(initial_transaction)
                        self._db_session.commit()

                    return redirect(url_for('login'))
                else:
                    error_message = result.get('message', 'Register failed')
                    return render_template('registration.html',
                                           error=error_message)
            return render_template('registration.html')

        @self._app.route('/logout')
        def logout() -> WerkzeugResponse:
            session.pop('user_id', None)
            return redirect(url_for('login'))

    def add_admin_user(self) -> None:
        """
        Makes all usernames lowercase,
        then adds a hardcoded admin user
        """
        all_users = self._db_session.query(User).all()
        for user in all_users:
            if user.username != user.username.lower():
                user.username = user.username.lower()
        self._db_session.commit()

        admin_username = 'admin'
        admin_password = 'admin'
        existing_admin = self._db_session.query(User).filter_by(
            username=admin_username.lower()).first()

        if not existing_admin:
            hashed_pw = bcrypt.hashpw(admin_password.encode('utf-8'),
                                      bcrypt.gensalt()).decode('utf-8')
            admin_user = User(username=admin_username.lower(),
                              password_hash=hashed_pw,
                              email='admin@example.com',
                              role=Role.admin)
            self._db_session.add(admin_user)
            self._db_session.commit()


def login_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to check if the user is logged in
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to check if the user is an admin before accessing certain routes.
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        user_id = session.get('user_id')
        user: Optional[User] = bank_app.db_session.query(User).filter_by(
            user_id=user_id).first()
        if not user or user.role != Role.admin:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


class Command(ABC):
    """
    Abstract base class representing a command that can be executed.
    """
    @abstractmethod
    def execute(self) -> None:
        pass


class DepositCommand(Command):
    def __init__(self, bank_system: BankSystem, user_id: int, account_id: int, amount: float) -> None:
        self._bank_system = bank_system
        self._user_id = user_id
        self._account_id = account_id
        self._amount = amount

    @property
    def amount(self) -> float:
        """Getter for the amount."""
        return self._amount

    @amount.setter
    def amount(self, value: float) -> None:
        """Setter for the amount."""
        self._amount = value

    def execute(self) -> None:
        """
        Execute the deposit operation.
        """
        self._bank_system.deposit(self._user_id,
                                  self._account_id,
                                  self._amount)  # type: ignore


class WithdrawCommand(Command):
    def __init__(self, bank_system: BankSystem, user_id: int, account_id: int, amount: float) -> None:
        self._bank_system = bank_system
        self._user_id = user_id
        self._account_id = account_id
        self._amount = amount

    @property
    def amount(self) -> float:
        """Getter for the amount."""
        return self._amount

    @amount.setter
    def amount(self, value: float) -> None:
        """Setter for the amount."""
        self._amount = value

    def execute(self) -> None:
        """
        Execute the withdraw operation.
        """
        self._bank_system.withdraw(self._user_id,
                                   self._account_id,
                                   self._amount)  # type: ignore


bank_app = BankApp()
app = bank_app.app  # to expose app to flaskCLI

if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True)

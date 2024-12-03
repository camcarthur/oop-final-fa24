import pytest
from logic.main import BankApp, WithdrawCommand, DepositCommand
from flask import Flask
from unittest.mock import Mock, patch, PropertyMock, MagicMock
from flask.sessions import SecureCookieSessionInterface
import bcrypt
import sqlalchemy.orm
from database.models import User, Account, Transaction, TransactionType, TransactionStatus, Role
from logic.user_auth import UserAuth
from logic.bank_system import BankSystem

@pytest.fixture
def client():
    bank_app = BankApp()
    bank_app.app.config['TESTING'] = True
    bank_app.app.config['SECRET_KEY'] = 'test_secret_key'

    # Mock the session interface to ensure it always opens a session.
    bank_app.app.session_interface = SecureCookieSessionInterface()

    with bank_app.app.test_client() as client:
        with bank_app.app.app_context():
            yield client

def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password
    })

def test_login_success(client):
    # Use a fixed hash for consistent testing
    fixed_hashed_password = bcrypt.hashpw('correct_password'.encode('utf-8'),
                                          bcrypt.gensalt()).decode('utf-8')

    with patch.object(sqlalchemy.orm.Session, 'query') as mock_query:
        # Mock the user returned by the database query
        mock_user = Mock()
        mock_user.username = 'correct_username'
        mock_user.password_hash = fixed_hashed_password
        mock_user.user_id = 1
        mock_user.role = Role.user
        mock_query.return_value.\
            filter_by.return_value.first.return_value = mock_user

        response = client.post('/login', data={
            'username': 'correct_username',
            'password': 'correct_password'
        })
        # Expecting a redirect on successful login
        assert response.status_code == 302
        assert "/dashboard" in response.headers['Location']

def test_login_fail(client):
    response = client.post('/login', data=dict
                           (username="wrong", password="wrong"))
    assert response.status_code == 401
    assert b"Invalid username or password" in response.data

def test_register_success(client):
    with patch.object(sqlalchemy.orm.Session, 'query') as mock_query:
        # Simulate no existing user
        mock_query.return_value.\
            filter_by.return_value.first.return_value = None

        with patch.object(sqlalchemy.orm.Session, 'add') as mock_add:
            with patch.object(sqlalchemy.orm.Session, 'commit') as mock_commit:
                # Mock user availability after creation
                mock_new_user = Mock()
                mock_new_user.user_id = 1
                mock_query.return_value.\
                    filter_by.return_value.first.side_effect =\
                    [None, mock_new_user]

                response = client.post('/register', data={
                    'username': 'new_user',
                    'email': 'new_user@example.com',
                    'password': 'new_password'
                })
                assert response.status_code == 302
                assert response.headers.get('Location', '')\
                    .endswith("/login") or response.headers.\
                    get('Location', '').endswith("/")
                mock_add.assert_called()
                mock_commit.assert_called()

def test_dashboard_access_without_login(client):
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert response.headers.get('Location', '').endswith("/login") \
        or response.headers.get('Location', '').endswith("/")

def test_dashboard_access_with_login(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Dashboard" in response.data

def test_logout(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers.get('Location', '').endswith("/login") \
        or response.headers.get('Location', '').endswith("/")

def test_transfer_insufficient_funds(client):
    with patch.object(sqlalchemy.orm.Session, 'query') as mock_query:
        mock_user = Mock()
        mock_user.user_id = 1
        mock_account = Mock()
        type(mock_account).balance = PropertyMock(return_value=100.0)

        def mock_query_side_effect(model):
            if model == User:
                return Mock(filter_by=Mock(return_value=Mock(first=Mock
                            (return_value=mock_user))))
            elif model == Account:
                return Mock(filter_by=Mock(return_value=Mock(first=Mock
                            (return_value=mock_account))))
            return None

        mock_query.side_effect = mock_query_side_effect

        # Patch add_admin_user to prevent TypeError
        with patch.object(BankApp, 'add_admin_user', return_value=None):
            bank_app_instance = BankApp()
            bank_app_instance._db_session = MagicMock()
            bank_app_instance._db_session.query.return_value.filter_by\
                .return_value.first.return_value = mock_account
            bank_app_instance.app.config['TESTING'] = True
            bank_app_instance.app.config['SECRET_KEY'] = 'test_secret_key'

            with bank_app_instance.app.test_client() as client:
                with bank_app_instance.app.app_context():
                    with client.session_transaction() as sess:
                        sess['user_id'] = 1

                    response = client.post('/transfer', data={
                        'fromAccount': '1',
                        'transferType': 'internal',
                        'amount': '200',  # More than the account balance
                        'toInternalAccount': '2'
                    })
                    assert response.status_code == 400
                    assert b"Insufficient funds." in response.data

def test_transfer_external_success(client):
    with patch.object(sqlalchemy.orm.Session, 'query') as mock_query:
        # Mock user and accounts
        mock_user = Mock()
        mock_user.user_id = 1
        mock_user.username = 'test_user'
        mock_user.role = Role.user

        mock_from_account = Mock()
        mock_from_account.account_id = 1
        mock_from_account.user_id = 1
        mock_from_account.balance = 500.0

        mock_to_account = Mock()
        mock_to_account.account_id = 2
        mock_to_account.user_id = 2
        mock_to_account.balance = 300.0

        def mock_query_side_effect(model):
            if model == User:
                return Mock(filter_by=Mock(return_value=Mock(
                    first=Mock(return_value=mock_user))))
            elif model == Account:
                def filter_by_side_effect(*args, **kwargs):
                    account_id = kwargs.get('account_id')
                    if account_id == 1:
                        return Mock(first=Mock(return_value=mock_from_account))
                    elif account_id == 2:
                        return Mock(first=Mock(return_value=mock_to_account))
                    else:
                        return Mock(first=Mock(return_value=None))
                return Mock(filter_by=Mock(side_effect=filter_by_side_effect))
            return None

        mock_query.side_effect = mock_query_side_effect

        # Patch add_admin_user to prevent TypeError
        with patch.object(BankApp, 'add_admin_user', return_value=None):
            bank_app_instance = BankApp()
            bank_app_instance._db_session = MagicMock()
            bank_app_instance._db_session.query.side_effect = mock_query_side_effect
            bank_app_instance.app.config['TESTING'] = True
            bank_app_instance.app.config['SECRET_KEY'] = 'test_secret_key'

            with bank_app_instance.app.test_client() as client:
                with bank_app_instance.app.app_context():
                    with client.session_transaction() as sess:
                        sess['user_id'] = 1

                    response = client.post('/transfer', data={
                        'fromAccount': '1',
                        'transferType': 'external',
                        'amount': '100',
                        'toExternalAccount': '2'
                    })
                    # Expecting a redirect to dashboard on success
                    assert response.status_code == 302
                    assert "/dashboard" in response.headers['Location']

def test_admin_access_with_admin_login(client):
    # Use the admin credentials
    with patch.object(sqlalchemy.orm.Session, 'query') as mock_query:
        hashed_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        mock_admin_user = Mock()
        mock_admin_user.username = 'admin'
        mock_admin_user.password_hash = hashed_password
        mock_admin_user.user_id = 1
        mock_admin_user.role = Role.admin

        mock_query.return_value.\
            filter_by.return_value.first.return_value = mock_admin_user

        # Login as admin
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin'
        })
        assert response.status_code == 302
        assert "/admin" in response.headers['Location']

        # Access admin page
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.get('/admin')
        assert response.status_code == 200
        assert b"Admin" in response.data

def test_admin_access_without_login(client):
    response = client.get('/admin')
    assert response.status_code == 302
    assert response.headers.get('Location', '').endswith("/login") \
        or response.headers.get('Location', '').endswith("/")

def test_admin_access_with_non_admin_login(client):
    # Use non-admin user credentials
    with patch.object(sqlalchemy.orm.Session, 'query') as mock_query:
        hashed_password = bcrypt.hashpw('userpass'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        mock_user = Mock()
        mock_user.username = 'user'
        mock_user.password_hash = hashed_password
        mock_user.user_id = 2
        mock_user.role = Role.user

        mock_query.return_value.\
            filter_by.return_value.first.return_value = mock_user

        # Login as regular user
        response = client.post('/login', data={
            'username': 'user',
            'password': 'userpass'
        })
        assert response.status_code == 302
        assert "/dashboard" in response.headers['Location']

        # Attempt to access admin page
        with client.session_transaction() as sess:
            sess['user_id'] = 2

        response = client.get('/admin')
        # Should redirect to login or dashboard
        assert response.status_code == 302
        assert response.headers.get('Location', '').endswith("/login") \
            or response.headers.get('Location', '').endswith("/")

def test_history_page_access_with_login(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.get('/history')
    assert response.status_code == 200
    assert b"Transaction History" in response.data

def test_history_page_access_without_login(client):
    response = client.get('/history')
    assert response.status_code == 302
    assert response.headers.get('Location', '').endswith("/login") or \
        response.headers.get('Location', '').endswith("/")

def test_api_transactions_with_login(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1

    # Mock the query for transactions
    with patch.object(sqlalchemy.orm.Session, 'query') as mock_query:
        mock_transaction = Mock()
        mock_transaction.account = Mock()
        mock_transaction.account.created_at.strftime.return_value = '2021-01-01'
        mock_transaction.transaction_type.name = 'Deposit'
        mock_transaction.account.account_type = 'Checking'
        mock_transaction.amount = 100.0

        mock_query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_transaction]

        response = client.get('/api/transactions')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert data[0]['type'] == 'Deposit'

def test_api_transactions_without_login(client):
    response = client.get('/api/transactions')
    assert response.status_code == 302
    assert response.headers.get('Location', '').endswith("/login") or \
        response.headers.get('Location', '').endswith("/")

def test_login_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Login" in response.data or b"Sign In" in response.data

def test_getters(client):
    bank_app_instance = BankApp()
    # Test the getters
    assert isinstance(bank_app_instance.app, Flask)
    assert bank_app_instance.db_session is not None
    assert isinstance(bank_app_instance.bank_system, BankSystem)
    assert isinstance(bank_app_instance.user_auth, UserAuth)

def test_deposit_command(client):
    # Mocking the BankSystem methods
    with patch.object(BankSystem, 'deposit') as mock_deposit:
        mock_deposit.return_value = None  # Simulate successful deposit

        # Mock user and account
        mock_user = Mock(user_id=1)
        mock_account = Mock(account_id=1, balance=500.00)

        # Create a mocked instance of BankSystem
        mock_bank_system = Mock()
        mock_bank_system.deposit = mock_deposit  # Assign mocked deposit method

        # Create DepositCommand instance with the mocked BankSystem
        deposit_command = DepositCommand(
            bank_system=mock_bank_system,  # Pass mocked BankSystem instance
            user_id=mock_user.user_id,
            account_id=mock_account.account_id,
            amount=100.0
        )

        # Test amount property getter and setter
        assert deposit_command.amount == 100.0
        deposit_command.amount = 150.0
        assert deposit_command.amount == 150.0

        # Execute the deposit
        deposit_command.execute()

        # Verify that the deposit method was called with correct parameters
        mock_deposit.assert_called_once_with(mock_user.user_id,
                                             mock_account.account_id, 150.0)
        assert mock_account.balance == 500.00

def test_withdraw_command(client):
    # Mocking the BankSystem methods
    with patch.object(BankSystem, 'withdraw') as mock_withdraw:
        mock_withdraw.return_value = None  # Simulate successful withdrawal

        # Mock user and account
        mock_user = Mock(user_id=1)
        mock_account = Mock(account_id=1, balance=500.00)

        # Create a mocked instance of BankSystem
        mock_bank_system = Mock()
        mock_bank_system.withdraw = mock_withdraw

        # Create WithdrawCommand instance with the mocked BankSystem
        withdraw_command = WithdrawCommand(
            bank_system=mock_bank_system,
            user_id=mock_user.user_id,
            account_id=mock_account.account_id,
            amount=100.0
        )

        # Test amount property getter and setter
        assert withdraw_command.amount == 100.0
        withdraw_command.amount = 80.0
        assert withdraw_command.amount == 80.0

        # Execute the withdraw
        withdraw_command.execute()

        # Verify that the withdraw method was called with correct parameters
        mock_withdraw.assert_called_once_with(
            mock_user.user_id, mock_account.account_id, 80.0)

        assert mock_account.balance == 500.00

def test_transfer_route_without_login(client):
    response = client.post('/transfer', data={
        'fromAccount': '1',
        'transferType': 'internal',
        'amount': '50',
        'toInternalAccount': '2'
    })
    assert response.status_code == 302
    assert response.headers.get('Location', '').endswith("/login") or \
        response.headers.get('Location', '').endswith("/")

def test_register_user_success():
    # Create a UserAuth instance with mocked BankSystem and Session
    mock_bank_system = Mock()
    mock_session = Mock()
    user_auth = UserAuth(mock_bank_system, mock_session)

    # Simulate successful user registration
    mock_session.query().filter_by().first.return_value = None
    result = user_auth.register_user("new_user", "email@example.com", "password")
    assert result['success'] is True

def test_bank_system_getter_setter():
    mock_bank_system = Mock()
    mock_session = Mock()
    user_auth = UserAuth(mock_bank_system, mock_session)
    assert user_auth.bank_system == mock_bank_system

    new_bank_system = Mock()
    user_auth.bank_system = new_bank_system
    assert user_auth.bank_system == new_bank_system

def test_session_getter_setter():
    mock_bank_system = Mock()
    mock_session = Mock()
    user_auth = UserAuth(mock_bank_system, mock_session)
    assert user_auth.session == mock_session

    new_session = Mock()
    user_auth.session = new_session
    assert user_auth.session == new_session

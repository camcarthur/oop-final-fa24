import pytest
from logic.user_auth import UserAuth
from unittest.mock import Mock


@pytest.fixture
def user_auth():
    session = Mock()
    bank_system = Mock()
    return UserAuth(bank_system, session)


def test_register_user_success(user_auth):
    user_auth.session.query().filter_by().first.return_value = None  # No existing user
    user_auth.session.commit.return_value = None
    result = user_auth.register_user(
        "new_user", "email@example.com", "password")
    assert result['success'] is True


def test_register_user_already_exists(user_auth):
    user_auth.session.query().filter_by().first.return_value = Mock()  # User already exists
    result = user_auth.register_user(
        "existing_user", "email@example.com", "password")
    assert result['success'] is False
    assert result['message'] == 'User already exists.'


def test_bank_system_getter_setter(user_auth):
    new_bank_system = Mock()
    user_auth.bank_system = new_bank_system
    assert user_auth.bank_system == new_bank_system


def test_session_getter_setter(user_auth):
    new_session = Mock()
    user_auth.session = new_session
    assert user_auth.session == new_session


def test_register_user_exception(user_auth):
    user_auth.session.query().filter_by().first.return_value = None
    user_auth.session.add.side_effect = Exception("Database error")
    result = user_auth.register_user(
        "new_user", "email@example.com", "password")
    assert result['success'] is False
    assert result['message'] == 'An error occurred while registering.'

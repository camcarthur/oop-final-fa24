import pytest
from logic.bank_system import BankSystem

@pytest.fixture
def bank_system():
    return BankSystem()

def test_deposit(bank_system):
    bank_system.accounts = {1: {1001: 100.0}}
    bank_system.deposit(1, 1001, 50.0)
    assert bank_system.accounts[1][1001] == 150.0

def test_withdraw_success(bank_system):
    bank_system.accounts = {1: {1001: 100.0}}
    bank_system.withdraw(1, 1001, 50.0)
    assert bank_system.accounts[1][1001] == 50.0

def test_withdraw_insufficient_funds(bank_system):
    bank_system.accounts = {1: {1001: 100.0}}
    bank_system.withdraw(1, 1001, 150.0)
    assert bank_system.accounts[1][1001] == 100.0

def test_transfer_funds_success(bank_system):
    bank_system.accounts = {1: {1001: 100.0, 1002: 50.0}}
    bank_system.transfer_funds(1, 1001, 1002, 50.0)
    assert bank_system.accounts[1][1001] == 50.0
    assert bank_system.accounts[1][1002] == 100.0

def test_transfer_funds_insufficient(bank_system):
    bank_system.accounts = {1: {1001: 100.0, 1002: 50.0}}
    bank_system.transfer_funds(1, 1001, 1002, 150.0)
    assert bank_system.accounts[1][1001] == 100.0
    assert bank_system.accounts[1][1002] == 50.0

def test_get_user_accounts(bank_system):
    bank_system.accounts = {1: {1001: 100.0}, 2: {2001: 50.0, 2002: 75.0}}
    user_1_accounts = bank_system.get_user_accounts(1)
    assert user_1_accounts == {1001: 100.0}
    user_3_accounts = bank_system.get_user_accounts(3)
    assert user_3_accounts == []

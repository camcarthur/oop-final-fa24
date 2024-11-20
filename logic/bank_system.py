class BankSystem:
    def __init__(self):
        self.accounts = {}  # Dictionary to store user accounts

    def get_user_accounts(self, user_id):
        return self.accounts.get(user_id, [])

    def deposit(self, user_id, account_id, amount):
        if user_id in self.accounts and account_id in self.accounts[user_id]:
            self.accounts[user_id][account_id] += amount

    def withdraw(self, user_id, account_id, amount):
        if user_id in self.accounts and account_id in self.accounts[user_id]:
            if self.accounts[user_id][account_id] >= amount:
                self.accounts[user_id][account_id] -= amount

    def transfer_funds(self, user_id, from_account, to_account, amount):
        if user_id in self.accounts:
            if from_account in self.accounts[user_id] and to_account in self.accounts[user_id]:
                if self.accounts[user_id][from_account] >= amount:
                    self.accounts[user_id][from_account] -= amount
                    self.accounts[user_id][to_account] += amount
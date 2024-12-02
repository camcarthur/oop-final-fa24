class BankSystem:
    def __init__(self):
        """
        Initialize BankSystem with a dictionary to store user accounts.
        """
        self._accounts = {}  # Dictionary to store user accounts

    @property
    def accounts(self):
        """Getter for user accounts."""
        return self._accounts

    @accounts.setter
    def accounts(self, value):
        """Setter for user accounts."""
        self._accounts = value

    def get_user_accounts(self, user_id):
        """
        Get accounts for a specific user.
        """
        return self._accounts.get(user_id, [])

    def deposit(self, user_id, account_id, amount):
        """
        Deposit an amount into the specified user account.
        """
        if user_id in self._accounts and account_id in self._accounts[user_id]:
            self._accounts[user_id][account_id] += amount

    def withdraw(self, user_id, account_id, amount):
        """
        Withdraw an amount from the specified user account if sufficient funds exist.
        """
        if user_id in self._accounts and account_id in self._accounts[user_id]:
            if self._accounts[user_id][account_id] >= amount:
                self._accounts[user_id][account_id] -= amount

    def transfer_funds(self, user_id, from_account, to_account, amount):
        """
        Transfer funds between two user accounts.
        """
        if user_id in self._accounts:
            if from_account in self._accounts[user_id] and to_account in self._accounts[user_id]:
                if self._accounts[user_id][from_account] >= amount:
                    self._accounts[user_id][from_account] -= amount
                    self._accounts[user_id][to_account] += amount
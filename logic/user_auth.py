class UserAuth:
    def __init__(self, bank_system):
        self.bank_system = bank_system
        self.users = {}  # Dictionary to store user information

    def register_user(self, username, password):
        if username in self.users:
            return {'success': False, 'message': 'Username already exists'}
        user_id = len(self.users) + 1  # Simple user ID generation
        self.users[username] = {'password': password, 'user_id': user_id}
        self.bank_system.accounts[user_id] = {}  # Create empty accounts for the user
        return {'success': True, 'message': 'User registered successfully'}

    def login_user(self, username, password):
        if username in self.users and self.users[username]['password'] == password:
            return self.users[username]
        return None
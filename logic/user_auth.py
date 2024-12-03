import bcrypt
from database.models import User, Role


class UserAuth:
    def __init__(self, bank_system, session):
        """
        Initialize UserAuth with bank system and database session.
        """
        self._bank_system = bank_system
        self._session = session

    @property
    def bank_system(self):
        """Getter for the bank system."""
        return self._bank_system

    @bank_system.setter
    def bank_system(self, value):
        """Setter for the bank system."""
        self._bank_system = value

    @property
    def session(self):
        """Getter for the database session."""
        return self._session

    @session.setter
    def session(self, value):
        """Setter for the database session."""
        self._session = value

    def register_user(self, username, email, password):
        """
        Register a new user with a hashed password and default role.
        """
        existing_user = self._session.query(User).filter_by(
            username=username).first()
        if existing_user:
            return {'success': False, 'message': 'User already exists.'}

        hashed_password = bcrypt.hashpw(password.encode('utf-8'),
                                        bcrypt.gensalt()).decode('utf-8')

        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=Role.user
        )

        try:
            self._session.add(new_user)
            self._session.commit()
            print(f"User {username} registered successfully.")
            return {'success': True}
        except Exception as e:
            self._session.rollback()
            print(f"Error adding user to the database: {e}")
            return {'success': False, 'message': 'An error occurred while\
                 registering.'}

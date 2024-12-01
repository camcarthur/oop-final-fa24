import bcrypt
from database.models import User, Role
from database.init_db import session

class UserAuth:
    def __init__(self, bank_system, session):
        """
        Initialize UserAuth with bank system and database session.
        """
        self._bank_system = bank_system
        self._session = session

    @property
    def session(self):
        """Getter for the database session."""
        return self._session

    def register_user(self, username, email, password):
        """
        Register a new user with a hashed password and default role.
        """
        # Check if the user already exists
        existing_user = self._session.query(User).filter_by(username=username).first()
        if existing_user:
            return {'success': False, 'message': 'User already exists.'}

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create a new user instance
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=Role.user
        )

        # Add the new user to the database and commit the transaction
        try:
            self._session.add(new_user)
            self._session.commit()
            print(f"User {username} registered successfully.")
            return {'success': True}
        except Exception as e:
            self._session.rollback()
            print(f"Error adding user to the database: {e}")
            return {'success': False, 'message': 'An error occurred while registering.'}
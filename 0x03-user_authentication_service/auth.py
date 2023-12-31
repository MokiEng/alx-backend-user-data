#!/usr/bin/env python3
"""A module for authentication-related routines.
"""
import bcrypt
import uuid
from typing import Union
from sqlalchemy.orm.exc import NoResultFound
from db import DB
from user import User


def _hash_password(password: str) -> bytes:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def _generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        """Initializes a new Auth instance."""
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Register a new user."""
        try:
            self._db.find_user_by(email=email)
        except NoResultFound:
            return self._db.add_user(email, _hash_password(password))
        raise ValueError("User {} already exists".format(email))

    def valid_login(self, email: str, password: str) -> bool:
        """Validate user login."""
        try:
            user = self._db.find_user_by(email=email)
            if bcrypt.checkpw(
                    password.encode('utf-8'),
                    user.hashed_password.encode('utf-8')):
                return True
            else:
                return False
        except Exception as e:
            return False

    def create_session(self, email: str) -> str:
        """Create a session ID for the user with the given email.
        """
        user = self._db.find_user_by(email=email)

        if user:
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        else:
            return None

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """Get user corresponding to the session ID."""
        user = None
        if session_id is None:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None
        return user

    def destroy_session(self, user_id: int):
        """Destroy session for the given user."""
        user = self._db.find_user_by(id=user_id)
        if user:
            user.session_id = None
            self._db.update_user(user)

    def get_reset_password_token(self, email: str) -> str:
        """Get reset password token for the given email."""
        user = None
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            user = None
        if user is None:
            raise ValueError()
        reset_token = _generate_uuid()
        self._db.update_user(user.id, reset_token=reset_token)
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """Updates a user's password given the user's reset token.
        """
        user = self._db.find_user_by(reset_token=reset_token)
        if not user:
            raise ValueError("Invalid reset token")

        hashed_password = self._hash_password(password)
        user.hashed_password = hashed_password
        user.reset_token = None
        self._db.update_user(user)

#!/usr/bin/env python3
"""Basic authentication module."""
import re
import base64
import binascii
from typing import Tuple, TypeVar

from .auth import Auth
from models.user import User


class BasicAuth(Auth):
    """a class BasicAuth that inherits from Auth.
    """
    def extract_base64_authorization_header(
            self,
            authorization_header: str) -> str:
        """A method that returns the Base64 part of the
        Authorization header for a Basic Authentication
        """
        if authorization_header is None:
            return None
        if not isinstance(authorization_header, str):
            return None
        if not authorization_header.startswith("Basic "):
            return None
        return authorization_header.split(" ", 1)[1]

    def decode_base64_authorization_header(
            self,
            base64_authorization_header: str,
            ) -> str:
        """A method that returns the decoded value of a Base64 string.
        """
        if base64_authorization_header is None:
            return None
        if not isinstance(base64_authorization_header, str):
            return None
        try:
            decoded_bytes = base64.b64decode(base64_authorization_header)
            return decoded_bytes.decode('utf-8')
        except binascii.Error:
            return None

    def extract_user_credentials(
            self,
            decoded_base64_authorization_header: str,
            ) -> Tuple[str, str]:
        """A method that returns the user email and password
        from the Base64 decoded value."""
        if type(decoded_base64_authorization_header) == str:
            pattern = r'(?P<user>[^:]+):(?P<password>.+)'
            field_match = re.fullmatch(
                pattern,
                decoded_base64_authorization_header.strip(),
            )
            if field_match is not None:
                user = field_match.group('user')
                password = field_match.group('password')
                return user, password
        return None, None

    def user_object_from_credentials(
            self,
            user_email: str,
            user_pwd: str) -> TypeVar('User'):
        """A method returns the User instance based on his email and password
        """
        if type(user_email) == str and type(user_pwd) == str:
            try:
                users = User.search({'email': user_email})
            except Exception:
                return None
            if len(users) <= 0:
                return None
            if users[0].is_valid_password(user_pwd):
                return users[0]
        return None

    def current_user(self, request=None) -> TypeVar('User'):
        """overloads Auth and retrieves the User instance for a request
        auth_header = self.authorization_header(request)
        b64_auth_token = self.extract_base64_authorization_header(auth_header)
        auth_token = self.decode_base64_authorization_header(b64_auth_token)
        email, password = self.extract_user_credentials(auth_token)
        return self.user_object_from_credentials(email, password)
        """
        if request is None:
            return None
        aut_header = self.authorization_header(request)
        decoded_header = self.decode_base64_authorization_header(aut_header)

        if not decoded_header:
            return None

        user_email, user_pwd = self.extract_user_credentials(decoded_header)
        if not user_email or not user_pwd:
            return None
        user = self.user_object_from_credentials(user_email, user_pwd)
        return user

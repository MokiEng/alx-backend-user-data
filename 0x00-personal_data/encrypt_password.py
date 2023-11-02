#!/usr/bin/env python3
"""Encrypting passwords module."""
import bcrypt


def hash_password(password: str) -> bytes:
    """Generate a random salt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return hashed_password


def is_valid(hashed_password: bytes, password: str) -> bool:
    """To implement the is_valid function that checks whether
    a provided password matches the hashed password.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

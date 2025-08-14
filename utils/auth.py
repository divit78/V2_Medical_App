

import hashlib

def hash_password(password: str) -> str:
    """
    Hashes a plain text password using SHA-256.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """
    Verifies a plain text password against the hashed one.
    """
    return hash_password(password) == hashed


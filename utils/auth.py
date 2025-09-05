
import hashlib


class PasswordManager:
    """Simple password management class"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a plain text password against the hashed one"""
        return PasswordManager.hash_password(password) == hashed


# Keep original functions for backward compatibility
def hash_password(password: str) -> str:
    """Hashes a plain text password using SHA-256"""
    return PasswordManager.hash_password(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verifies a plain text password against the hashed one"""
    return PasswordManager.verify_password(password, hashed)


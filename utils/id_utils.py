
import random

def generate_id(prefix):
    """
    Generate a unique ID using a given prefix and a random 5-digit number.
    """
    return f"{prefix}{random.randint(10000, 99999)}"



import random
import string
from datetime import datetime

def generate_compact_id(prefix: str = "HAP") -> str:
    """
    Generates a compact ID like HAP2023XXXXX
    """
    year = datetime.now().year
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{prefix}{year}{suffix}"

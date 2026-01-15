# Helper functions
import uuid
import os

def generate_unique_id():
    """Generates a unique string for sessions or claims."""
    return str(uuid.uuid4())

def format_currency(amount: float):
    """Simple helper to format repair costs later."""
    return f"${amount:,.2f}"

def ensure_dir(directory: str):
    """Ensures a directory exists before saving files to it."""
    if not os.path.exists(directory):
        os.makedirs(directory)
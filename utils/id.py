import random
import string

def generate_id(length=10, table=None):
    """
    Generate a random alphanumeric ID of specified length.
    If a table is provided, check if the ID already exists in the database.
    If it exists, generate a new ID until a unique one is found.
    [values]
    length (int): Length of the generated ID (default is 10).
    table (SQLAlchemy Table): SQLAlchemy table to check for existing IDs (default is None).
    [戻り値]
    str: A unique random alphanumeric ID.
    """
    while True:
        new_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        # Check if the ID already exists in the database
        if table is not None:
            existing_id = table.query.filter_by(id=new_id).first()
            if existing_id:
                # If it exists, generate a new ID
                continue
            else:
                # If it doesn't exist, return the new ID
                return new_id
        # If no table is provided, just return the new ID
        else:
            return new_id



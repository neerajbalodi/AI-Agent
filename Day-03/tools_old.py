from datetime import datetime
import secrets
import string


def get_current_date_time():
    return datetime.now()

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))



print(get_current_date_time())
password = generate_password()
print(password)
import bcrypt

def encrypt_pass(password: str) -> str:
    pass_encoded = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_pass = bcrypt.hashpw(pass_encoded, salt)
    return hashed_pass.decode('utf-8')  # return a string not bytes to store in DB

def check_encrypred_pass(password: str, hashed_pass:str) -> bool:
    """Verify if plaintext password matches the hashed password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_pass.encode('utf-8'))
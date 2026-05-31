from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# This is how we hash passwords
# bcrypt = special algorithm that makes passwords hard to crack
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This is the secret key used to sign JWT tokens
# Never share this! Keep it in .env
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"  # Algorithm to sign tokens

def hash_password(password: str) -> str:
    """
    Takes plain password, returns hashed version
    Example: "password123" → "$2b$12$abcdefg..."
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if plain password matches the hash
    Returns True if they match, False if not
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str, expires_delta: timedelta = None):
    """
    Creates a JWT token that contains user_id
    Token expires in 7 days by default
    """
    if expires_delta is None:
        expires_delta = timedelta(days=7)
    
    # Calculate when token expires
    expire = datetime.utcnow() + expires_delta
    
    # Data we put inside the token
    to_encode = {"sub": user_id, "exp": expire.timestamp()}
    
    # Sign the token with our secret key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> str:
    """
    Reads a JWT token and extracts the user_id
    If token is expired or fake, raises error
    Returns the user_id if valid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
        
        return user_id
    except JWTError:
        return None
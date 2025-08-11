# Simulating a JWT Generator from SP backend

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import jwt, JWTError

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY not set. Make sure your .env file is correct.")

def create_jwt_token(user_id: str):
    """Generates a valid, signed JWT for a given user ID."""
    # The payload contains the user_id (sub) and an expiration time (exp)
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=30)  # Token expires in 30 minutes
    }
    """
    for example, you can add more user information to the payload like this:
    payload_exam = {
        "sub": "user-001",
        "user_name": "Jane Doe",
        "email": "jane.doe@example.com",
        "premium_user": true,
        "exp": 1704065800
        }
    """
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

if __name__ == "__main__":
    test_user_id = "test-user-001"
    
    #generating the token
    token = create_jwt_token(test_user_id)
    
    print(f"Generated JWT for user '{test_user_id}':")
    print("---------------------------------------------------------------------")
    print(token)
    print("---------------------------------------------------------------------")
    print("\nCopy the token above and paste it into the `USER_JWT_TOKEN` variable in your HTML file.")

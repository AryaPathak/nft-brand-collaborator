import os
from cdp.auth.utils.jwt import generate_jwt, JwtOptions
from dotenv import load_dotenv

load_dotenv()

# Generate the JWT using the CDP SDK
jwt_token = generate_jwt(JwtOptions(
    api_key_id=os.getenv('KEY_NAME'),
    api_key_secret=os.getenv('KEY_SECRET'),
    request_method=os.getenv('REQUEST_METHOD'),
    request_host=os.getenv('REQUEST_HOST'),
    request_path=os.getenv('REQUEST_PATH'),
    expires_in=520  # optional (defaults to 120 seconds)
))

print(jwt_token)
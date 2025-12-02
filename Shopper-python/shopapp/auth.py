import os
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
import requests

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE')
ALGORITHMS = ["RS256"]

security = HTTPBearer()

def get_public_key():
    jwks_url = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
    try:
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching JWKS: {e}")
        return None

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    if not AUTH0_DOMAIN or not AUTH0_AUDIENCE:
        return {}

    token = credentials.credentials

    try:
        jwks = get_public_key()
        if not jwks:
            raise HTTPException(status_code=500, detail="Unable to fetch JWKS")

        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}

        for key in jwks.get("keys", []):
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer=f'https://{AUTH0_DOMAIN}/'
        )

        return payload

    except JWTError as e:
        print(f"JWT Error: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

def get_current_user(token_payload: dict = Depends(verify_token)) -> Optional[dict]:
    return token_payload

async def optional_verify_token(request: "Request") -> dict:
    from fastapi import Request as FastAPIRequest

    if not AUTH0_DOMAIN or not AUTH0_AUDIENCE:
        return {}

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {}

    try:
        from fastapi.security import HTTPAuthorizationCredentials
        token = auth_header.split(" ")[1]
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        return verify_token(credentials)
    except Exception:
        return {}

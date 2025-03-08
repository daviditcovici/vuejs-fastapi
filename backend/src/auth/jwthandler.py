from datetime import UTC, datetime, timedelta
import os

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from tortoise.exceptions import DoesNotExist

from src.database.models import Users
from src.schemas.token import TokenData
from src.schemas.users import UserOutSchema

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class OAuth2PasswordBearerCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request):
        authorization = request.cookies.get('Authorization', '')
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != 'bearer':
            if self.auto_error:
                raise HTTPException(status_code=401, detail="Not authenticated", headers={'WWW-Authenticate': 'Bearer'})
            return None

        return param


security = OAuth2PasswordBearerCookie('/login')


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def read_current_user(token = Depends(security)) -> UserOutSchema:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = await UserOutSchema.from_queryset_single(Users.get(username=token_data.username))
    except JWTError:
        raise credentials_exception
    except HTTPException:
        raise credentials_exception
    except DoesNotExist:
        raise credentials_exception
    except Exception:
        raise credentials_exception

    return user

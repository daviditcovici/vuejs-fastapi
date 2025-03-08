from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist

from src.database.models import Users
from src.schemas.users import UserInternalSchema

pw_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password):
    return pw_context.hash(password)


async def validate_user(user: OAuth2PasswordRequestForm = Depends()) -> UserInternalSchema:
    try:
        db_user = await UserInternalSchema.from_queryset_single(Users.get(username=user.username))
    except DoesNotExist:
        raise HTTPException(status_code=409, detail="Incorrect username or password")
    return db_user if pw_context.verify(user.password, db_user.password) else None

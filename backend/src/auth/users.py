from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist

from src.database.models import Users
from src.schemas.users import UserInternalSchema

pw_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password):
    return pw_context.hash(password)


async def validate_user(user: OAuth2PasswordRequestForm = Depends()):
    conflicting_cred_exception = HTTPException(status_code=409, detail="Incorrect username or password")

    try:
        db_user = await UserInternalSchema.from_queryset_single(Users.get(username=user.username))
    except DoesNotExist:
        raise conflicting_cred_exception

    if not pw_context.verify(user.password, db_user.password):
        raise conflicting_cred_exception
    return db_user

from fastapi import HTTPException
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist, IntegrityError

from src.database.models import Users
from src.schemas.users import UserOutSchema

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def create_user(user):
    user.password = pwd_context.encrypt(user.password)

    try:
        user_obj = await user.save()
    except IntegrityError:
        raise HTTPException(status_code=409, detail=f"Sorry, username {user.username} already exists")

    return await UserOutSchema.from_tortoise_orm(user_obj)


async def delete_user(user_id, current_user):
    forbidden_del_exception = HTTPException(status_code=403, detail=f"Not authorized to delete user {user_id}")

    try:
        db_user = await UserOutSchema.from_queryset_single(Users.get(id=user_id))
    except DoesNotExist:
        raise forbidden_del_exception

    if db_user.id != current_user.id:
        raise forbidden_del_exception
    await Users.filter(id=user_id).delete()

    return f"Deleted user {user_id}"

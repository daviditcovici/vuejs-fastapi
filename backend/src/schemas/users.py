from tortoise.contrib.pydantic import pydantic_model_creator

from src.database.models import Users

UserInSchema = pydantic_model_creator(
    Users, name='UserIn', exclude_readonly=True
)
UserOutSchema = pydantic_model_creator(
    Users, name='UserOut', exclude=('password', 'created_at', 'modified_at')
)
UserInternalSchema = pydantic_model_creator(
    Users, name='UserInternal', exclude=('created_at', 'modified_at')
)

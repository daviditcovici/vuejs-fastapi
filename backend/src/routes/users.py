from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.jwthandler import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, read_current_user
from src.auth.users import validate_user
import src.crud.users as users_crud
from src.schemas.token import Status
from src.schemas.users import UserOutSchema

router = APIRouter()


@router.get(path='/users/whoami', response_model=UserOutSchema, dependencies=[Depends(read_current_user)])
async def read_user_me(current_user=Depends(read_current_user)):
    return current_user


@router.post(path='/sign-up', response_model=UserOutSchema)
async def sign_up(user):
    return await users_crud.create_user(user)


@router.post('/sign-in')
async def sign_in(user: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await validate_user(user)
    except HTTPException:
        raise HTTPException(status_code=409, detail="Incorrect username or password",
                            headers={'WWW-Authenticate': 'Bearer'})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)

    token = jsonable_encoder(access_token)
    response = JSONResponse(content={'message': "You have successfully signed in. Welcome back!"})
    response.set_cookie(key='Authorization', value=f'Bearer {token}', max_age=1800, expires=1800, httponly=True)
    return response


@router.delete(path='/user/{user-id}', response_model=Status, responses={404: {'model': HTTPException}},
               dependencies=[Depends(read_current_user)])
async def delete_account(user_id: int, current_user=Depends(read_current_user)):
    return await users_crud.delete_user(user_id, current_user)

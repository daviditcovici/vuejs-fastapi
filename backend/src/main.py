from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from src.database.register import register_tortoise
from src.database.config import TORTOISE_ORM

Tortoise.init_models(['src.database.models'], 'models')

from src.routes import notes, users

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8080'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(notes.router)
app.include_router(users.router)

register_tortoise(app, config=TORTOISE_ORM, generate_schemas=False)


@app.get('/')
def home():
    return "Hello, World!"

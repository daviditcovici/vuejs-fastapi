from tortoise import Tortoise


def register_tortoise(
        app,
        config: dict = None,
        generate_schemas = False,
) -> None:
    @app.on_event('startup')
    async def init_orm():
        await Tortoise.init(config=config)
        if generate_schemas:
            await Tortoise.generate_schemas()

    @app.on_event('shutdown')
    async def close_orm():
        await Tortoise.close_connections()

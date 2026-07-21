import asyncio

from sqlalchemy import text

from app.database.session import engine


async def check_connection():
    async with engine.connect() as conn:
        result = await conn.execute(text("select 1"))
        value = result.scalar_one()
    await engine.dispose()
    return value


if __name__ == "__main__":
    print(asyncio.run(check_connection()))

import asyncpg
from config import DATABASE_URL

pool = None


async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=10,
        command_timeout=60,
    )

    async with pool.acquire() as connection:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (,
                id BIGINT PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
        )


async def add_user(user_id: int, username: str, full_name: str):
    async with pool.acquire() as connection:
        await connection.execute(
            """
            INSERT INTO users (id, username, full_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (id) DO NOTHING;
            """,
            user_id,
            username,
            full_name,
        )
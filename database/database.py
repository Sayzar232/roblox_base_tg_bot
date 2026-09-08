import asyncpg
from config import DATABASE_URL

pool = None

USER_TYPE_USER = "user"
USER_TYPE_SCAMMER = "scammer"
USER_TYPE_GARANT = "garant"


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
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
        )

        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_ranks (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                rank_name TEXT,
                purchased_at TIMESTAMP DEFAULT NOW(),
                expires_at TIMESTAMP
            );
            """
        )

        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_garants (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                garant_name TEXT,
                roblox_username TEXT,
                proofs TEXT,
                proofs_num INT,
                purchased_at TIMESTAMP DEFAULT NOW(),
                expires_at TIMESTAMP
            );
            """
        )

        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_scammers (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                reason TEXT NOT NULL,
                proofs TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
        )


async def get_user_type(user_id: int) -> str:
    async with pool.acquire() as connection:
        is_scammer = await connection.fetchval(
            """
            SELECT 1
            FROM user_scammers
            WHERE user_id = $1
            LIMIT 1;
            """,
            user_id,
        )
        if is_scammer is not None:
            return USER_TYPE_SCAMMER

        is_garant = await connection.fetchval(
            """
            SELECT 1
            FROM user_garants
            WHERE user_id = $1
              AND (expires_at IS NULL OR expires_at > NOW())
            LIMIT 1;
            """,
            user_id,
        )
        if is_garant is not None:
            return USER_TYPE_GARANT

    return USER_TYPE_USER


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
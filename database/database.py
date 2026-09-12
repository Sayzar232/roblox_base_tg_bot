import asyncpg
import json
import random
import string

from config import DATABASE_URL

pool = None

USER_TYPE_USER = "Обычный пользователь"
USER_TYPE_SCAMMER = "Скаммер"
USER_TYPE_GARANT = "Гарант"

POST_COLORS = ("danger", "success", "primary")


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

        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                text TEXT,
                photo_file_id TEXT,
                buttons JSONB,
                is_favorite BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
        )


async def get_user_type(user_id: int) -> str:
    async with pool.acquire() as connection:
        user_data = await connection.fetchrow(
            """
            SELECT username, full_name
            FROM users
            WHERE id = $1;
            """,
            user_id,
        )

        if user_data is None:
            return USER_TYPE_USER, "user", "Пользователь"

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
            return USER_TYPE_SCAMMER, user_data["username"], user_data["full_name"]

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
            return USER_TYPE_GARANT, user_data["username"], user_data["full_name"]

    return USER_TYPE_USER, user_data["username"], user_data["full_name"]


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


def generate_post_id(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))


async def create_post(user_id: int, text: str, photo_file_id: str, buttons: list) -> str:
    async with pool.acquire() as connection:
        # Получает Id, которого еще нет
        while True:
            post_id = generate_post_id()

            is_exists = await connection.fetchval(
                """
                SELECT 1
                FROM posts
                WHERE id = $1;
                """,
                post_id,
            )
            if is_exists is None:
                break

        await connection.execute(
            """
            INSERT INTO posts (id, user_id, text, photo_file_id, buttons)
            VALUES ($1, $2, $3, $4, $5::jsonb);
            """,
            post_id,
            user_id,
            text,
            photo_file_id,
            json.dumps(buttons) if buttons else None,
        )

        return post_id


async def get_post(post_id: str):
    async with pool.acquire() as connection:
        return await connection.fetchrow(
            """
            SELECT id, user_id, text, photo_file_id, buttons
            FROM posts
            WHERE id = $1;
            """,
            post_id,
        )


async def get_favorite_posts(user_id: int) -> list:
    async with pool.acquire() as connection:
        return await connection.fetch(
            """
            SELECT id, text
            FROM posts
            WHERE user_id = $1
              AND is_favorite = TRUE
            ORDER BY created_at DESC;
            """,
            user_id,
        )


async def set_post_favorite(post_id: str, is_favorite: bool = True):
    async with pool.acquire() as connection:
        await connection.execute(
            """
            UPDATE posts
            SET is_favorite = $2
            WHERE id = $1;
            """,
            post_id,
            is_favorite,
        )
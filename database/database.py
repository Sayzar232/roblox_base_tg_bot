import asyncpg
import json
import random
import string

from config import (
    DATABASE_URL,
    USER_TYPE_USER,
    USER_TYPE_SCAMMER,
    USER_TYPE_GARANT,
    USER_TYPE_TRUSTED_GARANT,
    POST_COLORS
)

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


async def get_user_id_by_username(username: str):
    """Находит ID пользователя по @username (без учета регистра). Возвращает None, если не найден."""
    username = username.lstrip("@").lower()

    async with pool.acquire() as connection:
        user_id = await connection.fetchval(
            """
            SELECT id
            FROM users
            WHERE lower(username) = $1;
            """,
            username,
        )

    return user_id


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
            return USER_TYPE_USER, None, None

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

        garant_name = await connection.fetchval(
            """
            SELECT garant_name
            FROM user_garants
            WHERE user_id = $1
              AND (expires_at IS NULL OR expires_at > NOW())
            LIMIT 1;
            """,
            user_id,
        )
        if garant_name is not None:
            return garant_name, user_data["username"], user_data["full_name"]

    return USER_TYPE_USER, user_data["username"], user_data["full_name"]


async def get_user_info(user_id: int):
    """Возвращает информацию о пользователе из дополнительной таблицы.

    Если пользователь скаммер — возвращает данные из user_scammers,
    если гарант (и гарантство ещё действительно) — из user_garants.
    Если пользователь не найден или является обычным пользователем — возвращает None.
    """
    async with pool.acquire() as connection:
        scammer = await connection.fetchrow(
            """
            SELECT u.username, u.full_name, s.reason, s.proofs, s.created_at
            FROM user_scammers s
            JOIN users u ON u.id = s.user_id
            WHERE s.user_id = $1
            ORDER BY s.created_at DESC
            LIMIT 1;
            """,
            user_id,
        )
        if scammer is not None:
            return {
                "user_type": USER_TYPE_SCAMMER,
                "username": scammer["username"],
                "full_name": scammer["full_name"],
                "reason": scammer["reason"],
                "proofs": scammer["proofs"],
                "created_at": scammer["created_at"],
            }

        garant = await connection.fetchrow(
            """
            SELECT u.username, u.full_name, g.garant_name, g.roblox_username,
                   g.proofs, g.proofs_num, g.purchased_at, g.expires_at
            FROM user_garants g
            JOIN users u ON u.id = g.user_id
            WHERE g.user_id = $1
              AND (g.expires_at IS NULL OR g.expires_at > NOW())
            ORDER BY g.purchased_at DESC
            LIMIT 1;
            """,
            user_id,
        )
        if garant is not None:
            return {
                "user_type": garant["garant_name"] or USER_TYPE_GARANT,
                "username": garant["username"],
                "full_name": garant["full_name"],
                "roblox_username": garant["roblox_username"],
                "proofs": garant["proofs"],
                "proofs_num": garant["proofs_num"],
                "purchased_at": garant["purchased_at"],
                "expires_at": garant["expires_at"],
            }

    return None


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


async def get_admin_stats() -> dict:
    """Собирает статистику бота для админ панели."""
    async with pool.acquire() as connection:
        users = await connection.fetchval("SELECT COUNT(*) FROM users;")
        users_today = await connection.fetchval(
            """
            SELECT COUNT(*)
            FROM users
            WHERE created_at >= CURRENT_DATE;
            """
        )
        garants = await connection.fetchval(
            """
            SELECT COUNT(DISTINCT user_id)
            FROM user_garants
            WHERE expires_at IS NULL OR expires_at > NOW();
            """
        )
        scammers = await connection.fetchval(
            """
            SELECT COUNT(DISTINCT user_id)
            FROM user_scammers;
            """
        )
        posts = await connection.fetchval("SELECT COUNT(*) FROM posts;")

    return {
        "users": users or 0,
        "users_today": users_today or 0,
        "garants": garants or 0,
        "scammers": scammers or 0,
        "posts": posts or 0,
    }


async def add_user_garant(user_id: int, garant_name: str = None, roblox_username: str = None, proofs: str = None, proofs_num: str = None):
    """Выдаёт пользователю звание гаранта (бессрочно)."""
    async with pool.acquire() as connection:
        await connection.execute(
            """
            INSERT INTO user_garants (user_id, garant_name, roblox_username, proofs, proofs_num)
            VALUES ($1, $2, $3, $4, $5);
            """,
            user_id,
            garant_name,
            roblox_username,
            proofs,
            proofs_num,
        )


async def add_user_scammer(user_id: int, reason: str, proofs: str = "Нет информации"):
    """Добавляет пользователя в скаммеры."""
    async with pool.acquire() as connection:
        await connection.execute(
            """
            INSERT INTO user_scammers (user_id, reason, proofs)
            VALUES ($1, $2, $3);
            """,
            user_id,
            reason,
            proofs,
        )
import psycopg2
import psycopg2.extras
from utils.logger import get_logger

logger = get_logger(__name__)

class Storage:
    def __init__(self):
        self.conn = None

    async def connect(self):
        self.conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres123",
            database="postgres"
        )
        self.conn.autocommit = True
        logger.info("PostgreSQL-ге қосылды")

    async def save_user(self, username: str, full_name: str, user_id: int = None):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (user_id, username, full_name, message_count, last_active)
                VALUES (%s, %s, %s, 1, NOW())
                ON CONFLICT (user_id) DO UPDATE
                SET message_count = users.message_count + 1,
                    last_active = NOW(),
                    username = EXCLUDED.username,
                    full_name = EXCLUDED.full_name
                """,
                (user_id, username, full_name)
            )

    async def save_message(self, username: str, user_message: str, bot_response: str, user_id: int = None):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages (user_id, user_message, bot_response)
                VALUES (%s, %s, %s)
                """,
                (user_id, user_message, bot_response)
            )

    async def get_chat_history(self, username: str):
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT m.user_message, m.bot_response
                FROM messages m
                JOIN users u ON m.user_id = u.user_id
                WHERE u.username = %s
                ORDER BY m.created_at DESC
                LIMIT 10
                """,
                (username,)
            )
            rows = cur.fetchall()
            history = []
            for row in reversed(rows):
                history.append({"role": "user", "content": row["user_message"]})
                history.append({"role": "assistant", "content": row["bot_response"]})
            return history

    async def get_user_role(self, user_id: int) -> str:
        with self.conn.cursor() as cur:
            cur.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            return row[0] if row else "student"

    async def set_user_role(self, user_id: int, role: str):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET role = %s WHERE user_id = %s",
                (role, user_id)
            )

storage = Storage()
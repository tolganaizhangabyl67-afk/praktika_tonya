import psycopg2
import psycopg2.extras
import csv
import io
import logging

logger = logging.getLogger(__name__)

ROLE_PERMISSIONS = {
    "student": ["get_user_stats"],
    "teacher": ["get_user_stats", "query_users"],
    "admin": ["get_user_stats", "query_users", "export_to_csv"]
}

def get_db_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres123",
        database="postgres"
    )

async def get_user_role(user_id: int) -> str:
    try:
        conn = get_db_connection()
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
        conn.close()
        return row["role"] if row else "student"
    except Exception as e:
        logger.error("get_user_role қатесі: " + str(e))
        return "student"

def check_permission(role: str, action: str) -> bool:
    return action in ROLE_PERMISSIONS.get(role, [])

async def query_users(user_id: int) -> str:
    role = await get_user_role(user_id)
    if not check_permission(role, "query_users"):
        return "⛔ Қатынас тыйым салынған. Ролыңыз: " + role + ". Қажетті рол: teacher немесе admin."
    try:
        conn = get_db_connection()
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT user_id, username, full_name, message_count, role FROM users ORDER BY message_count DESC")
            rows = cur.fetchall()
        conn.close()
        if not rows:
            return "Пайдаланушылар жоқ."
        result = "Пайдаланушылар:\n\n"
        for r in rows:
            result += "• " + str(r["full_name"]) + " (@" + str(r["username"]) + ") — " + str(r["message_count"]) + " хабарлама [" + str(r["role"]) + "]\n"
        return result
    except Exception as e:
        return "Қате: " + str(e)

async def get_user_stats(user_id: int) -> str:
    role = await get_user_role(user_id)
    if not check_permission(role, "get_user_stats"):
        return "⛔ Қатынас тыйым салынған. Ролыңыз: " + role
    try:
        conn = get_db_connection()
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
        conn.close()
        if not row:
            return "Пайдаланушы табылмады."
        return (
            "Статистика:\n"
            "Аты: " + str(row["full_name"]) + "\n"
            "Username: @" + str(row["username"]) + "\n"
            "Рол: " + str(row["role"]) + "\n"
            "Хабарламалар: " + str(row["message_count"]) + "\n"
            "Тіркелген: " + row["created_at"].strftime("%d.%m.%Y") + "\n"
            "Соңғы белсенділік: " + row["last_active"].strftime("%d.%m.%Y %H:%M")
        )
    except Exception as e:
        return "Қате: " + str(e)

async def export_to_csv(user_id: int) -> str:
    role = await get_user_role(user_id)
    if not check_permission(role, "export_to_csv"):
        return "⛔ Қатынас тыйым салынған. Ролыңыз: " + role + ". Қажетті рол: admin."
    try:
        conn = get_db_connection()
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM users ORDER BY created_at")
            rows = cur.fetchall()
        conn.close()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "user_id", "username", "full_name", "role", "message_count", "created_at", "last_active"])
        for r in rows:
            writer.writerow([r["id"], r["user_id"], r["username"], r["full_name"], r["role"], r["message_count"], r["created_at"], r["last_active"]])
        return output.getvalue()
    except Exception as e:
        return "Қате: " + str(e)
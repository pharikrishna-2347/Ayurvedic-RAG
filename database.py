import sqlite3
import bcrypt

def get_connection():
    return sqlite3.connect(
        "chat_history.db",
        check_same_thread=False
    )

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats(
id INTEGER PRIMARY KEY AUTOINCREMENT,
role TEXT,
content TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT,
    content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

conn.commit()

def register_user(username,password):

    import bcrypt

    conn = get_connection()

    cursor = conn.cursor()

    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    try:

        cursor.execute("""
        INSERT INTO users(
            username,
            password
        )
        VALUES(?,?)
        """,(username,hashed))

        conn.commit()

        conn.close()

        return True

    except:

        conn.close()

        return False
def login_user(username,password):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT id,password
    FROM users
    WHERE username=?
    """,(username,))

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return None

    user_id = user[0]
    stored_hash = user[1]

    import bcrypt

    if bcrypt.checkpw(
        password.encode(),
        stored_hash
    ):
        return user_id

    return None
def save_message(user_id,role,content):

    cursor.execute("""
    INSERT INTO messages(
        user_id,
        role,
        content
    )
    VALUES(?,?,?)
    """,(user_id,role,content))

    conn.commit()

def load_chat(user_id):

    cursor.execute("""
    SELECT role,content
    FROM messages
    WHERE user_id=?
    ORDER BY id
    """,(user_id,))

    rows = cursor.fetchall()

    return [
        {
            "role":role,
            "content":content
        }
        for role,content in rows
    ]
def get_recent_context(messages):

    return messages[-20:]
from .database import get_db


def create_user(username: str, hashed_password: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (username, hashed_password) VALUES (%s, %s) RETURNING id, username;
            """, (username, hashed_password))
            user = cur.fetchone()
            conn.commit()
            return user


def authenticate_user(username: str, password: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, username, hashed_password FROM users WHERE username = %s;
            """, (username,))
            user = cur.fetchone()
            return user


def get_likes(username: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.track_id, t.track_name, t.artist_name, t.year, t.relevance_percentage
                FROM likes l
                JOIN users u ON l.user_id = u.id
                JOIN tracks t ON l.track_id = t.id
                WHERE u.username = %s;
            """, (username,))
            tracks = cur.fetchall()
            return tracks


def get_dislikes(username: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.track_id, t.track_name, t.artist_name, t.year, t.relevance_percentage
                FROM dislikes d
                JOIN users u ON d.user_id = u.id
                JOIN tracks t ON d.track_id = t.id
                WHERE u.username = %s;
            """, (username,))
            tracks = cur.fetchall()
            return tracks


def upload_csv(username: str, track_ids: list):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
            user = cur.fetchone()
            if not user:
                return False
            user_id = user['id']
            for track_id in track_ids:
                cur.execute("""
                    INSERT INTO likes (user_id, track_id) VALUES (%s, %s);
                """, (user_id, track_id))
            conn.commit()
            return True


def add_like(username: str, track_id: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
            user = cur.fetchone()
            if not user:
                return False
            user_id = user['id']
            cur.execute("""
                INSERT INTO likes (user_id, track_id) VALUES (%s, %s);
            """, (user_id, track_id))
            conn.commit()
            return True


def add_dislike(username: str, track_id: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
            user = cur.fetchone()
            if not user:
                return False
            user_id = user['id']
            cur.execute("""
                INSERT INTO dislikes (user_id, track_id) VALUES (%s, %s);
            """, (user_id, track_id))
            conn.commit()
            return True


def remove_like(username: str, track_id: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
            user = cur.fetchone()
            if not user:
                return False
            user_id = user['id']
            cur.execute("""
                DELETE FROM likes WHERE user_id = %s AND track_id = %s;
            """, (user_id, track_id))
            conn.commit()
            return True


def remove_dislike(username: str, track_id: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
            user = cur.fetchone()
            if not user:
                return False
            user_id = user['id']
            cur.execute("""
                DELETE FROM dislikes WHERE user_id = %s AND track_id = %s;
            """, (user_id, track_id))
            conn.commit()
            return True


def get_recommendations():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT track_id, track_name, artist_name, year, relevance_percentage
                FROM tracks
                ORDER BY relevance_percentage DESC;
            """)
            tracks = cur.fetchall()
            return tracks

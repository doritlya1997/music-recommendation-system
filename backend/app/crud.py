from .database import get_db


def create_user(username: str, hashed_password: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (username, hashed_password) VALUES (%s, %s) RETURNING id as user_id, username as user_name;
            """, (username, hashed_password))
            user = cur.fetchone()
            conn.commit()
            return user


def authenticate_user(username: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id as user_id, username as user_name, hashed_password FROM users WHERE username = %s;
            """, (username,))
            user = cur.fetchone()
            return user

# TODO: reprocess the data and produce simple 'year' column
def get_likes(user_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.track_id, t.track_name, t.artist_name, 0 as year, concat('https://open.spotify.com/track/', t.track_id) as link
                FROM likes l
                JOIN users u ON l.user_id = u.id
                JOIN tracks t ON l.track_id = t.track_id
                WHERE u.id = %s
                ORDER BY l.update_timestamp DESC;
            """, (user_id,))
            tracks = cur.fetchall()
            return tracks


def get_liked_tracks(user_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT tracks.*, update_timestamp
                FROM likes
                JOIN tracks ON likes.track_id = tracks.track_id
                WHERE likes.user_id = %s; 
                """, (user_id,))
            tracks = cur.fetchall()
            return tracks


def get_dislikes(user_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.track_id, t.track_name, t.artist_name, 0 as year, concat('https://open.spotify.com/track/', t.track_id) as link
                FROM dislikes d
                JOIN users u ON d.user_id = u.id
                JOIN tracks t ON d.track_id = t.track_id
                WHERE u.id = %s
                ORDER BY d.update_timestamp DESC;
            """, (user_id,))
            tracks = cur.fetchall()
            return tracks


def get_disliked_tracks(user_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT tracks.*, update_timestamp
                FROM dislikes
                JOIN tracks ON dislikes.track_id = tracks.track_id
                WHERE dislikes.user_id = %s; 
                """, (user_id,))
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


def add_like(user_id: int, track_id: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
            user = cur.fetchone()
            if not user:
                return False
            cur.execute("""INSERT INTO likes (user_id, track_id) VALUES (%s, %s);""", (user_id, track_id))
            conn.commit()
            return True


def add_dislike(user_id: int, track_id: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
            user = cur.fetchone()
            if not user:
                return False
            cur.execute("""INSERT INTO dislikes (user_id, track_id) VALUES (%s, %s);""", (user_id, track_id))
            conn.commit()
            return True


def remove_like(user_id: int, track_id: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
            user = cur.fetchone()
            if not user:
                return False
            cur.execute("""DELETE FROM likes WHERE user_id = %s AND track_id = %s;""", (user_id, track_id))
            conn.commit()
            return True


def remove_dislike(user_id: int, track_id: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
            user = cur.fetchone()
            if not user:
                return False
            cur.execute("""DELETE FROM dislikes WHERE user_id = %s AND track_id = %s;""", (user_id, track_id))
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

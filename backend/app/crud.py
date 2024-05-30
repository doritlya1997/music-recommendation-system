from .database import get_db


def user_exists(user_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
            user = cur.fetchone()
            return user is not None


def create_user(username: str, hashed_password: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (username, hashed_password) VALUES (%s, %s)
                ON CONFLICT (username) DO NOTHING
                RETURNING id as user_id, username as user_name;
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


def get_likes(user_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.track_id, t.track_name, t.artist_name, year
                FROM likes l
                JOIN users u ON l.user_id = u.id
                JOIN tracks t ON l.track_id = t.track_id
                WHERE u.id = %s
                ORDER BY l.update_timestamp ASC;
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
                SELECT t.track_id, t.track_name, t.artist_name, year
                FROM dislikes d
                JOIN users u ON d.user_id = u.id
                JOIN tracks t ON d.track_id = t.track_id
                WHERE u.id = %s
                ORDER BY d.update_timestamp ASC;
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


def add_like(user_id: int, track_id: str):
    if not user_exists(user_id):
        return False, "User does not exist."

    with get_db() as conn:
        with conn.cursor() as cur:
            # Check if the track_id exists in the dislikes table for the user
            cur.execute("""
                SELECT 1 FROM dislikes WHERE user_id = %s AND track_id = %s;
            """, (user_id, track_id))
            disliked = cur.fetchone()
            if disliked:
                return False, "Track is in dislikes, cannot add to likes."

            # Insert into likes if not in dislikes
            cur.execute("""
                INSERT INTO likes (user_id, track_id) 
                VALUES (%s, %s)
                ON CONFLICT (user_id, track_id) DO NOTHING;
            """, (user_id, track_id))
            conn.commit()
            affected_rows = cur.rowcount
            if affected_rows > 0:
                return True, "Track added to likes."
            else:
                return False, "Track already in likes."


def upload_csv(user_id: int, track_ids: list):
    if not user_exists(user_id):
        return False

    affected_rows = 0
    for track_id in track_ids:
        if add_like(user_id, track_id)[0]:
            affected_rows += 1
    return affected_rows


def add_dislike(user_id: int, track_id: str):
    if not user_exists(user_id):
        return False

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO dislikes (user_id, track_id) 
                VALUES (%s, %s)
                ON CONFLICT (user_id, track_id) DO NOTHING;
            """, (user_id, track_id))
            conn.commit()
            return True


def remove_like(user_id: int, track_id: str):
    if not user_exists(user_id):
        return False

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""DELETE FROM likes WHERE user_id = %s AND track_id = %s;""", (user_id, track_id))
            conn.commit()
            return True


def remove_dislike(user_id: int, track_id: str):
    if not user_exists(user_id):
        return False

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""DELETE FROM dislikes WHERE user_id = %s AND track_id = %s;""", (user_id, track_id))
            conn.commit()
            return True


# Recommendations


def get_tracks_by_id_and_score(top_tracks: list[tuple]):
    values_clause = ", ".join([f"('{track_id}', {relevance_percentage})" for track_id, relevance_percentage in top_tracks])
    query = f"""
        SELECT track_id, track_name, artist_name, relevance_percentage, year
        FROM tracks
        JOIN (
            SELECT track_id_col, ROUND(100 * relevance_percentage, 2) as relevance_percentage
            FROM (
                VALUES {values_clause}
            ) AS derived_table(track_id_col, relevance_percentage)
        ) AS recommended
        ON tracks.track_id = recommended.track_id_col;"""
    # print(query)

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            tracks = cur.fetchall()
            return tracks

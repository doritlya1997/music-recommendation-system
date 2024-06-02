from typing import Optional,List, Dict
from .database import get_db

def sign_up_report(user_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                            INSERT INTO user_events (user_id, event_id) 
                            VALUES (%s, %s);
                        """, (user_id, 1))
            conn.commit()


def user_logged_in_report(user_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                            INSERT INTO user_events (user_id, event_id) 
                            VALUES (%s, %s);
                        """, (user_id, 2))
            conn.commit()


def user_added_track_report(user_id: int, track_id: str) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                            INSERT INTO user_events (user_id, event_id, track_id) 
                            VALUES (%s, %s, %s);
                        """, (user_id, 3, track_id))
            conn.commit()


def user_liked_recommended_track_report(user_id: int, track_id: str, recommendation_type: Optional[str] = None) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                            INSERT INTO user_events (user_id, event_id, track_id, recommendation_type) 
                            VALUES (%s, %s, %s, %s);
                        """, (user_id, 4, track_id, recommendation_type))
            conn.commit()


def user_disliked_recommended_track_report(user_id: int, track_id: str, recommendation_type: str) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                            INSERT INTO user_events (user_id, event_id, track_id, recommendation_type) 
                            VALUES (%s, %s, %s, %s);
                        """, (user_id, 5, track_id, recommendation_type))
            conn.commit()


def user_requested_recommendations_report(user_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                            INSERT INTO user_events (user_id, event_id) 
                            VALUES (%s, %s);
                        """, (user_id, 6))
            conn.commit()



def user_ignored_recommendations_report(user_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                            INSERT INTO user_events (user_id, event_id) 
                            VALUES (%s, %s);
                        """, (user_id, 7))
            conn.commit()


def get_user_event_counts() -> List[Dict[str, int]]:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT event_name, COUNT(*) as event_count
                FROM user_events
                JOIN events_definitions ON user_events.event_id = events_definitions.event_id
                GROUP BY event_name;
            """)
            result = cur.fetchall()
            return [{"event_name": row[0], "event_count": row[1]} for row in result]


def get_most_liked_tracks(limit: int = 10) -> List[Dict[str, int]]:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT track_id, COUNT(*) as like_count
                FROM user_events
                WHERE event_id = 4  -- user_liked_recommended_track
                GROUP BY track_id
                ORDER BY like_count DESC
                LIMIT %s;
            """, (limit,))
            result = cur.fetchall()
            return [{"track_id": row[0], "like_count": row[1]} for row in result]


def get_user_activity() -> List[Dict[str, int]]:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT user_id, COUNT(*) as activity_count
                FROM user_events
                GROUP BY user_id
                ORDER BY activity_count DESC;
            """)
            result = cur.fetchall()
            return [{"user_id": row[0], "activity_count": row[1]} for row in result]

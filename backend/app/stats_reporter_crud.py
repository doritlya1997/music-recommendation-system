from typing import Optional

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
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


def load_ENV_VAR():
    load_dotenv()

    DATABASE_URL = os.getenv("DATABASE_URL")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

    print(f"DATABASE_URL={DATABASE_URL}")
    print(f"PINECONE_API_KEY={PINECONE_API_KEY}")


@contextmanager
def get_db():
    load_ENV_VAR()
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    except Exception as e:
        print(e)
    finally:
        conn.close()


@contextmanager
def get_pinecone_conn():
    load_ENV_VAR()
    pc = Pinecone(api_key=PINECONE_API_KEY)
    conn = pc.Index('tracks')
    try:
        yield conn
    except Exception as e:
        print(e)
    finally:
        # Explicitly delete the connection object
        del conn

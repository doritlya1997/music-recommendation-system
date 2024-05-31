import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

DATABASE_URL="postgres://ghiabcwcxsyfvo:9de383d33fe38cec6d6bb1f41fa313df2f054cc6091bd08cb018f02e74c0cdd7@ec2-34-252-152-193.eu-west-1.compute.amazonaws.com:5432/d9mck4patkc46n"
PINECONE_API_KEY="248cf0f2-be45-4f5e-9854-67884f601c89"

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    except Exception as e:
        print(e)
    finally:
        conn.close()


@contextmanager
def get_pinecone_conn():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    conn = pc.Index('tracks')
    try:
        yield conn
    except Exception as e:
        print(e)
    finally:
        # Explicitly delete the connection object
        del conn
from .database import get_pinecone_conn


# Query Pinecone 'tracks' index, using 'cosine' metric, to find the top most similar vectors
def query_pinecone(column_averages: list[float], top_k: int):
    with get_pinecone_conn() as conn:
        query_result = conn.query(vector=column_averages, top_k=top_k)
        return query_result

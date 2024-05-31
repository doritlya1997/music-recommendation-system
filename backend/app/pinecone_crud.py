from .database import get_pinecone_index


# Query Pinecone 'tracks' index, using 'cosine' metric, to find the top most similar vectors
def query_pinecone_by_vector(index_name: str, column_averages: list[float], top_k: int):
    with get_pinecone_index(index_name) as index:
        query_result = index.query(vector=column_averages, top_k=top_k)
        return query_result


def query_pinecone_by_ids(index_name: str, id_list: list[str]):
    with get_pinecone_index(index_name) as index:
        fetch_results = index.fetch(ids=id_list)
        return fetch_results

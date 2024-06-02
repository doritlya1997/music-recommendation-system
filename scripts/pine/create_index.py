from pinecone import Pinecone, ServerlessSpec

PINECONE_API_KEY = "***"


def preprocess():
    pc = Pinecone(api_key=PINECONE_API_KEY)

    pc.create_index(
        name="tracks",
        dimension=16,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

    pc.create_index(
        name="users",
        dimension=16,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )


if __name__ == "__main__":
    preprocess()

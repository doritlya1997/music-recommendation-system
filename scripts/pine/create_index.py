from pinecone import Pinecone, ServerlessSpec

PINECONE_API_KEY = "248cf0f2-be45-4f5e-9854-67884f601c89"


def preprocess():
    pc = Pinecone(api_key=PINECONE_API_KEY)

    pc.create_index(
        name="tracks",
        dimension=16, # Replace with your model dimensions
        metric="cosine", # Replace with your model metric
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )


if __name__ == "__main__":
    preprocess()

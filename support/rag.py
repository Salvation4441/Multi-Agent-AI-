# PHASE 1

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


# initialize chromadb client
client  =  chromadb.PersistentClient(path="./chroma_db")

embedding_func = DefaultEmbeddingFunction()

# create collection
collection  = client.get_or_create_collection(
    name = "coolbreeze_docs",
    embedding_function= embedding_func
)



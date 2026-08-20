# PHASE 1

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import os
from pypdf import PdfReader


# initialize chromadb client
client  =  chromadb.PersistentClient(path="./chroma_db")

embedding_func = DefaultEmbeddingFunction()

# create collection
collection  = client.get_or_create_collection(
    name = "coolbreeze_docs",
    embedding_function= embedding_func
)


# putting docs into chuncks
def chunk_text(text, chunk_size=500):
    # chunks = [i will learn python]  --> i will learn python
    chunks = []
    current_chunk = []
    current_size = 0
    words = text.split()

    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1  # +1 for the space

        if current_size >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0

    # add the last chunk if it is not empty
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks
            

# load documents
def load_documents():
    docs_path = "support/documents/"
    
    documents = []
    ids = []

    for filename in os.listdir(docs_path):
        if filename.endswith(".pdf"):
            filepath = os.path.join(docs_path,filename)
            reader = PdfReader(filepath)

            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            chunks = chunk_text(text)
            
            # generating the ids
            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                ids.append(f"{filename}_{i}")
    
    if documents:
        collection.add(documents = documents,ids = ids)
    

    print(f"Loaded {len(documents)} documents into ChromaDB")




        
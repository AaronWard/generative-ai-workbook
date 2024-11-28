# query_db.py

import os
import chromadb
from chromadb.utils import embedding_functions
import openai

# Set your OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Initialize ChromaDB client with persistent storage
persist_directory = './chromadb'  # Same as in store_vector.py
client = chromadb.PersistentClient(path=persist_directory)

# Define the embedding function using OpenAI's embeddings
embedding_function = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai.api_key,
    model_name='text-embedding-ada-002'
)

# Use the same key as in store_vector.py
key = 'youtube_videos'
collection_name = f'memory-{key}'

# Get the collection
collection = client.get_collection(
    name=collection_name,
    embedding_function=embedding_function
)

def query_database(query_text, n_results=5):
    """
    Query the vector database for relevant documents.
    
    Args:
        query_text (str): The query string to search for.
        n_results (int): Number of top results to retrieve.

    Returns:
        list: A list of dictionaries containing document content and metadata.
    """
    # Perform the query
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    # Format the results
    documents = []
    for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
        documents.append({
            "content": doc,
            "metadata": metadata
        })
    
    return documents

if __name__ == "__main__":
    # Prompt user for a query
    query_text = input("Enter your query: ")
    n_results = int(input("Enter the number of results to retrieve (default is 5): ") or 5)
    
    # Query the database
    results = query_database(query_text, n_results)
    
    # Display results
    if results:
        print("\nQuery Results:")
        for i, result in enumerate(results):
            print(f"\nResult {i + 1}:")
            print("Content:", result["content"])
            print("Metadata:", result["metadata"])
    else:
        print("No results found.")

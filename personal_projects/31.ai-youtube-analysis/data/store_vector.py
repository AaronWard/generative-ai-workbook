# store_vector.py

import os
import json
import chromadb
from chromadb.utils import embedding_functions
import openai

# Set your OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Initialize ChromaDB client with persistent storage
persist_directory = './chromadb'  # Update this path
client = chromadb.PersistentClient(path=persist_directory)

# Define the embedding function using OpenAI's embeddings
embedding_function = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai.api_key,
    model_name='text-embedding-ada-002'
)

# Use the same key as in ControlFlow Memory
key = 'youtube_videos'
collection_name = f'memory-{key}'

# Create or get the collection
collection = client.get_or_create_collection(
    name=collection_name,
    embedding_function=embedding_function
)

# Directory containing your JSON files
data_dir = '../ui/src/data'  # Update this path

# Iterate over each JSON file in the directory
for filename in os.listdir(data_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(data_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in file {file_path}: {e}")
                continue

            # Handle single document case
            if isinstance(data, dict):
                data = [data]  # Convert single document into a list

            # Ensure data is a list of documents
            if not isinstance(data, list):
                print(f"Invalid JSON structure in file {file_path}: Expected a list or a single document.")
                continue

            for doc in data:
                # Skip invalid documents
                if not isinstance(doc, dict):
                    print(f"Skipping invalid document in file {file_path}: {doc}")
                    continue

                # Generate a unique ID using the video URL
                doc_id = doc.get('url')
                if not doc_id:
                    print(f"Skipping document with no URL in file {file_path}: {doc}")
                    continue

                # Combine text fields for embedding
                text_fields = [
                    doc.get('title', ''),
                    doc.get('summary', ''),
                    doc.get('description', ''),
                    ', '.join(doc.get('categories', []))  # Join categories into a string
                ]
                content = '\n'.join(filter(None, text_fields))

                if not content.strip():
                    print(f"Skipping document with no content in file {file_path}: {doc}")
                    continue

                # Metadata for the document
                metadata = {
                    'title': doc.get('title'),
                    'url': doc.get('url'),
                    'published_at': doc.get('published_at'),
                    'categories': ', '.join(doc.get('categories', [])),  # Convert list to string
                    'channel': doc.get('channel'),
                    'channelIcon': doc.get('channelIcon'),
                }

                # Add the document to the collection
                collection.add(
                    documents=[content],
                    metadatas=[metadata],
                    ids=[doc_id]
                )

print("All valid documents have been stored in the vector database.")

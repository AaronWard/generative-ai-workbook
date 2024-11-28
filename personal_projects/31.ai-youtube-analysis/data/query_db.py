import os
import chromadb
from chromadb.utils import embedding_functions
import openai
import controlflow as cf
# Import the custom ChromaMemory
from CustomChromaMemory import CustomChromaMemory

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

# Create the CustomChromaMemory provider for ControlFlow
provider = CustomChromaMemory(
    client=client,
    collection_name=collection_name,
    embedding_function=embedding_function
)

# Create the Memory object
memory = cf.Memory(
    key=key,
    instructions="""
    This memory stores information about YouTube videos, including their titles, summaries, descriptions, and categories.
    - Use this memory to retrieve information about videos when needed.
    - Add to this memory when new video data is available.
    """,
    provider=provider
)

# Define the ControlFlow agent
agent = cf.Agent(
    name="YouTube Assistant",
    instructions="""
    You are a helpful assistant that provides information about YouTube videos. you must ONLY use the provided documents 
    to inform your responses.\n Otherwise, say you do have any record in your knowledge base. Provide dates for events you talk about in your response.
    """,
    memories=[memory]
)

def query_database_and_respond(query_text, n_results=5):
    """
    Query the vector database for relevant documents and use an agent to generate a response.
    
    Args:
        query_text (str): The query string to search for.
        n_results (int): Number of top results to retrieve.

    Returns:
        str: Agent's response to the query with links to relevant videos.
    """
    # Query the database
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    # Format the retrieved documents for the agent
    links = []  # To store video URLs
    if 'documents' in results and results['documents']:
        retrieved_docs = []
        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            retrieved_docs.append(f"Content: {doc}\nMetadata: {metadata}")
            if 'url' in metadata:
                links.append(metadata['url'])
    else:
        retrieved_docs = ["No relevant documents found."]
    
    # Combine retrieved documents into context for the agent
    context = "\n\n".join(retrieved_docs)
    
    # Use the ControlFlow agent to generate a response
    agent_response = cf.run(
        f"The user asked: {query_text}\n\nBased on the following retrieved documents:\n\n{context}\n\nReally capture the essence of the query and the context.",
        agents=[agent]
    )
    
    # Add links to the response
    if links:
        links_text = "\n".join([f"- {link}" for link in links])
        agent_response += f"\n\nIf you're interested in more, you should take a look at these videos:\n{links_text}"
    
    return agent_response

if __name__ == "__main__":
    # Prompt user for a query
    query_text = input("Enter your query: ")
    n_results = 2
    
    # Get the response from the RAG system
    response = query_database_and_respond(query_text, n_results)
    
    # Display the response
    print("\nAgent Response:")
    print(response)

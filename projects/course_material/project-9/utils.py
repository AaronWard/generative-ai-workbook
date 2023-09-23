from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone, Chroma
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import pinecone
import asyncio
from langchain.document_loaders.sitemap import SitemapLoader


# Function to fetch data from website
# https://python.langchain.com/docs/modules/data_connection/document_loaders/integrations/sitemap
def get_website_data(sitemap_url):
    print('Pulling website data...')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loader = SitemapLoader(
        sitemap_url
    )

    docs = loader.load()

    return docs

# Function to split data into smaller chunks
def split_data(docs):
    print('Splitting data into documents...')
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    docs_chunks = text_splitter.split_documents(docs)
    return docs_chunks

# Function to create embeddings instance
def create_embeddings():
    print('Creating embeddings...')
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return embeddings

# Function to push data to Pinecone
def push_to_pinecone(pinecone_apikey, pinecone_environment, pinecone_index_name, embeddings, docs):
    print('Pushing data to Pinecone...')
    pinecone.init(
        api_key=pinecone_apikey,
        environment=pinecone_environment
    )

    index_name = pinecone_index_name
    index = Pinecone.from_documents(docs, embeddings, index_name=index_name)
    return index

def push_to_chroma(docs, embeddings, persist_directory="./chroma_db"):
    '''
    returns a chromadb vector representation store  
    instance of documents

    Args:
        - docs (list): chunks of documents.
        - embeddings (): some embedding function
    Returns:
        - db (Chroma.from_documents): 
    '''
    return Chroma.from_documents(docs, embeddings, persist_directory=persist_directory)

def pull_from_chroma(embeddings,  persist_directory="./chroma_db"):
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)

def pull_from_pinecone(pinecone_apikey, pinecone_environment, pinecone_index_name, embeddings):
    print('Pulling data from Pinecone...')

    pinecone.init(
        api_key=pinecone_apikey,
        environment=pinecone_environment
    )
    
    index_name = pinecone_index_name

    return Pinecone.from_existing_index(index_name, embeddings)

# This function will help us in fetching the top relevent documents from our vector store - Pinecone Index
def get_similar_docs(db, query, k=2):
    print('Performing similarity search...')
    similar_docs = db.similarity_search(query, k=k)
    return similar_docs


if __name__ == "__main__":
    pass
"""
This Script loads in a bunch of txt files, in this case speeches of US presidents, and
stores the embeddings in a Chroma vector database. The script takes an argument called query
in which you can make general questions about the documents. For example:

- "Who mentioned war the most times, and what was the context?"
- "Who has the most negative sounding speech?"

https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/directory_loader.html?highlight=directoryloader
https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/chroma.html
https://github.com/hwchase17/chroma-langchain/blob/master/persistent-qa.ipynb

data: https://millercenter.org/sites/default/files/corpus/presidential-speeches.json

Required
- brew install libmagic
- pip install tiktoken

"""
import os
import nltk
import argparse
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

from langchain import OpenAI, VectorDBQA
from langchain.vectorstores import Chroma
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter

load_dotenv(find_dotenv())
# Turn strings into a vector space
embeddings = OpenAIEmbeddings()

data_path = Path("..", "data", "speeches_txt").expanduser()
db_path = str(Path("~", "Desktop", "db").expanduser())

def create_embeddings(data_path, db_path, embeddings):
    """
    Load the txt files using glob and create Chroma vector store

    Args:
        - data_path:
        - db_path:
        - embeddings:
    Return:
        vectordb:
    """

    loader = DirectoryLoader(data_path, glob="**/*.txt")
    docs = loader.load()

    # break the text into chunks of 1000
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(docs)

    # Initialize Vector Store
    vector_db = Chroma.from_documents(
        documents=texts, embedding=embeddings, persist_directory=db_path)
    vector_db.persist()
    print(f"Embeddings stored in a persistent location at: {db_path}")

    return vectordb


def load_embeddings(db_path, embeddings):
    """
    Load vector store

    Args:
        - db_path
        - embeddings
    Returns:
        - vectordb
    """
    vectordb = Chroma(persist_directory=db_path, embedding_function=embeddings)
    return vectordb

def query_LLM(vector_db, args):
    """
    Query the OpenAI LLM with the vectore store information
    
    """

    qa = VectorDBQA.from_chain_type(llm=OpenAI(), chain_type="stuff", vectorstore=vector_db)
    print(qa.run(args.query))


if __name__ == "__main__":

    # Pass question as argument
    parser = argparse.ArgumentParser(
        description="Argument Parse"
    )

    parser.add_argument(
        "--query", type=str, help="Question for the LLM", required=True
    )

    args = parser.parse_args()

    # Create the embeddings if they don't exist, otherwise load them
    if Path(db_path, 'chroma-embeddings.parquet').exists() and Path(db_path, 'chroma-embeddings.parquet').exists():
        vectordb = load_embeddings(db_path=db_path, embeddings=embeddings)
    else:
        vectordb = create_embeddings(data_path=data_path, db_path=db_path, embeddings=embeddings)

    # Query the model with a question
    query_LLM(vectordb, args)



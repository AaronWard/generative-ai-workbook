"""
Pull documents from passing a URL, pull down the webpages
with beautifulsoup, embed and store docs in vectorstore

Also has the ability to query the documents you've stored
using vector representations of your query ie: similarity_search()

"""

import os
import constants
from utils import (get_website_data, split_data, create_embeddings,
                   push_to_chroma, pull_from_chroma, get_similar_docs)
import streamlit as st
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

load_dotenv(Path('../../.env'))

# Creating Session State Variable
if 'HUGGINGFACEHUB_API_TOKEN' not in st.session_state:
    st.session_state['HUGGINGFACEHUB_API_TOKEN'] = os.environ['HUGGINGFACEHUB_API_TOKEN']

st.title('🤖 Webpage Document Search') 

#********SIDE BAR Funtionality started*******

# Sidebar to capture the API keys
st.sidebar.write(f"## Load data to from {constants.WEBSITE_URL} to Chroma")
load_button = st.sidebar.button("Upload", key="load_button")

db = None
embeddings=create_embeddings()

#If the bove button is clicked, pushing the data to Chroma...
if load_button:
    #Proceed only if API keys are provided
    if st.session_state['HUGGINGFACEHUB_API_TOKEN'] != "":

        #Fetch data from site
        site_data=get_website_data(constants.WEBSITE_URL)
        st.write("Data pull done...")

        #Split data into chunks
        chunks_data=split_data(site_data)
        st.write("Spliting data done...")

        db = push_to_chroma(chunks_data, embeddings)
        st.write("Pushing data to Chroma done...")
        st.sidebar.success("Data pushed to Chroma successfully!")
    else:
        st.sidebar.error("Ooopssss!!! Please provide API keys.....")

#********SIDE BAR Funtionality ended*******

#Captures User Inputs
prompt = st.text_input('How can I help you my friend ❓', key="prompt")  # The box for the text prompt
document_count = st.slider('How many links should I return? 🔗', 0, 5, 2, step=1)
submit = st.button("Search") 


if submit:
    print('Search submitted')
    #Proceed only if API keys are provided
    if st.session_state['HUGGINGFACEHUB_API_TOKEN'] != "":
        if db == None:
            st.sidebar.error("Documents have not yet been embedded.")
        else:
            #Fetch relavant documents from Pinecone index
            relavant_docs = get_similar_docs(db, prompt, document_count)
            st.write(relavant_docs)

            #Displaying search results
            st.success("Please find the search results :")
            #Displaying search results
            st.write("search results list....")
            for document in relavant_docs:
                st.write("👉**Result : " + str(relavant_docs.index(document)+1)+"**")
                st.write("**Info**: " + document[0].page_content)
                st.write("**Link**: " + document[0].metadata['source'])
    else:
        st.sidebar.error("Please provide API keys.")



   

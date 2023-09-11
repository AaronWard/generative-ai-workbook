import os
import constants
from utils import *
import streamlit as st
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

load_dotenv(Path('../../.env'))

# Creating Session State Variable
if 'HUGGINGFACEHUB_API_TOKEN' not in st.session_state:
    st.session_state['HUGGINGFACEHUB_API_TOKEN'] = os.environ['HUGGINGFACEHUB_API_TOKEN']
if 'gcp-starter' not in st.session_state:
    st.session_state['gcp-starter'] = os.environ['gcp-starter']

st.title('🤖 AI Assistance For Website') 

#********SIDE BAR Funtionality started*******

# Sidebar to capture the API keys
st.sidebar.title("Load data to Pinecone")
load_button = st.sidebar.button("Upload", key="load_button")

#If the bove button is clicked, pushing the data to Pinecone...
if load_button:
    #Proceed only if API keys are provided
    if st.session_state['HUGGINGFACEHUB_API_TOKEN'] != "" and st.session_state['gcp-starter']!= "" :

        #Fetch data from site
        site_data=get_website_data(constants.WEBSITE_URL)
        st.write("Data pull done...")

        #Split data into chunks
        chunks_data=split_data(site_data)
        st.write("Spliting data done...")

        #Creating embeddings instance
        embeddings=create_embeddings()
        st.write("Embeddings instance creation done...")

        #Push data to Pinecone
        print(constants.PINECONE_ENVIRONMENT, constants.PINECONE_INDEX)
        push_to_pinecone(st.session_state['gcp-starter'], 
                         constants.PINECONE_ENVIRONMENT,
                         constants.PINECONE_INDEX, 
                         embeddings,
                         chunks_data
                )
        
        st.write("Pushing data to Pinecone done...")
        st.sidebar.success("Data pushed to Pinecone successfully!")
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
    if st.session_state['HUGGINGFACEHUB_API_TOKEN'] != "" and st.session_state['gcp-starter']!= "" :

        #Creating embeddings instance
        embeddings=create_embeddings()
        st.write("Embeddings instance creation done...")

        #Pull index data from Pinecone
        index = pull_from_pinecone(
                            st.session_state['gcp-starter'], 
                            constants.PINECONE_ENVIRONMENT,
                            constants.PINECONE_INDEX, 
                            embeddings
                        )
        st.write("Pinecone index retrieval done...")

        #Fetch relavant documents from Pinecone index
        relavant_docs = get_similar_docs(index,prompt,document_count)
        st.write(relavant_docs)

        #Displaying search results
        st.success("Please find the search results :")
         #Displaying search results
        st.write("search results list....")
        for document in relavant_docs:
            st.write("👉**Result : "+ str(relavant_docs.index(document)+1)+"**")
            st.write("**Info**: "+document.page_content)
            st.write("**Link**: "+ document.metadata['source'])
    else:
        st.sidebar.error("Ooopssss!!! Please provide API keys.....")


   

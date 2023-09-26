import streamlit as st
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

load_dotenv(Path('../../.env'))
load_dotenv()

from utils import query_agent


st.title("CSV Querying")
st.header("Please upload your CSV file here:")

# Capture the CSV file
data = st.file_uploader("Upload CSV file", type="csv")

query = st.text_area("Enter your query")
button = st.button("Generate Response")

if button:
    # Get Response
    answer =  query_agent(data,query)
    st.write(answer)
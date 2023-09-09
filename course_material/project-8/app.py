import os
import pandas as pd
import streamlit as st
from pathlib import Path
from utils import generate_script
from dotenv import find_dotenv, load_dotenv

load_dotenv(Path('../../.env'))

# Applying Styling
st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #0099ff;
    color:#ffffff;
}
div.stButton > button:hover {
    background-color: #00ff00;
    color:#FFFFFF;
    }
</style>""", unsafe_allow_html=True)

# Creating Session State Variable
if 'API_Key' not in st.session_state:
    st.session_state['API_Key'] = os.environ['OPENAI_API_KEY']

st.title('❤️ YouTube Script Writing Tool') 

# Sidebar to capture the OpenAi API key
st.sidebar.title("Upload files for additional context")
data = st.sidebar.file_uploader("Upload CSV file", type=["txt", "csv", "json", "md", "xls", "xlsx"])
st.sidebar.image('./Youtube.jpg', width=300, use_column_width=True)

data_text = ""
if data is not None:
    file_details = {"File Name": data.name, "File Type": data.type, "File Size": data.size}
    st.write(file_details)

    # Check file type and read file accordingly
    if data.type == "text/plain":
        data_text = data.read().decode("utf-8")
    elif data.type == "application/vnd.ms-excel":
        # Assume it's a csv
        df = pd.read_csv(data)
        data_text = df.to_string()
    elif data.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(data)
        data_text = df.to_string()
    elif data.type == "application/json":
        import json
        data = json.load(data)
        data_text = json.dumps(data, indent=4)
    else:
        st.warning("Unsupported file type: {}".format(data.type))


# Captures User Inputs
prompt = st.text_input('Please provide the topic of the video', key="prompt")
video_length = st.text_input('Expected Video Length 🕒 (in minutes)', key="video_length")
creativity = st.slider('Words limit ✨ - (0 LOW || 1 HIGH)', 0.0, 1.0, 0.2, step=0.1)

submit = st.button("Generate Script for me")
if submit:
    if st.session_state['API_Key']:

        search_result, title, script = generate_script(prompt, data_text, video_length, creativity, st.session_state['API_Key'])
        st.success('Hope you like this script ❤️')

        st.subheader("Title:🔥")
        st.write(title)

        st.subheader("Your Video Script:📝")
        st.write(script)

        st.subheader("Check Out - Provided Data:")
        with st.expander('Show me 👀'): 
            st.info(data_text)

        st.subheader("Check Out - DuckDuckGo Search:🔍")
        with st.expander('Show me 👀'): 
            st.info(search_result)
    else:
        st.error("Please provide API key.....")

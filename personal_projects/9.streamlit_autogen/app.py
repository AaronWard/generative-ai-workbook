import time
import threading
import streamlit as st
from agent import StreamlitAgent

# Function to update the UI
state_lock = threading.Lock()

def update_ui(runner_msg, assistant_msg):
    with state_lock:
        try:
            if 'messages' not in st.session_state:
                st.session_state.messages = []

            new_messages = [
                {"content": runner_msg['content'], "is_user": False},
                {"content": assistant_msg['content'], "is_user": False}
            ]
            st.session_state.messages.extend(new_messages)
        except Exception as e:
            print(f"Error updating UI: {str(e)}")

        # Trigger rerun to refresh UI
        st.rerun()

def main():
    st.set_page_config(
        page_title="Autogen X Streamlit 👾",
        page_icon="👾",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={'About': "# Autogen x Streamlit"}
    )
    st.title("Autogen X Streamlit 👾")

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    response_container = st.container()
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_area("Your question goes here:", key='input', height=100)
            submit_button = st.form_submit_button(label='Send')

            if submit_button:
                st.session_state.messages.append({"content": user_input, "is_user": True})
                agent = StreamlitAgent()
                agent.run(user_input, update_ui)  
    
    # Move the message display outside the form block
    with response_container:
        for msg in st.session_state.get('messages', []):
            is_user = msg["is_user"]
            content = msg["content"]
            if is_user:
                st.text(f"You: {content}")
            else:
                st.text(f"Agent: {content}")

if __name__ == '__main__':
    main()
import time
import threading
import streamlit as st
from queue import Empty, Queue
from agent import StreamlitAgent
from streamlit_chat import message

# Function to update the UI
state_lock = threading.Lock()

# Function to update the UI
def update_ui(runner_msg, assistant_msg):
    # Add messages from the agent to the session state
    st.session_state.messages.extend([
        {"content": runner_msg['content'], "is_user": False},
        {"content": assistant_msg['content'], "is_user": False}
    ])
    # Trigger rerun to refresh UI
    st.rerun()

# Function to listen for messages from the agent and update the UI
def message_listener(queue, callback):
    while True:
        try:
            runner_msg, assistant_msg = queue.get(timeout=1)
            callback(runner_msg, assistant_msg)
        except Empty:
            time.sleep(0.1)
        except Exception as e:
            print(f"Error in message_listener: {str(e)}")

def main():
    # Set up Streamlit configuration
    st.set_page_config(
        page_title="Autogen X Streamlit 👾",
        page_icon="👾",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={'About': "# Autogen x Streamlit"}
    )
    st.title("Autogen X Streamlit 👾")

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
                message_queue = Queue()
                        
                agent = StreamlitAgent()
                # Here the agent is run and responses are placed in message_queue
                agent.run(user_input, update_ui)  
                        
                # Start a thread that listens for messages from the agent and updates the UI
                listener_thread = threading.Thread(target=message_listener, args=(message_queue, update_ui))
                listener_thread.start()

    with response_container:
        for i, msg in enumerate(st.session_state.get('messages', [])):
            is_user = msg["is_user"]
            content = msg["content"]
            if is_user:
                message(f"You: {content}", is_user=True, key=f"user_msg_{i}")
            else:
                message(f"Agent: {content}", is_user=False, key=f"agent_msg_{i}")

if __name__ == '__main__':
    main()
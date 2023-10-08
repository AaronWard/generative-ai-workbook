import time
import threading
import streamlit as st
from queue import Empty, Queue
from agent import StreamlitAgent
from streamlit_chat import message

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


def message_listener(queue):
    while True:
        try:
            # Non-blocking get from queue, with a timeout to prevent it from blocking indefinitely
            runner_msg, assistant_msg = queue.get(timeout=1)
            with state_lock:
                
    
                st.session_state.messages.extend([
                    {"content": runner_msg['content'], "is_user": False},
                    {"content": assistant_msg['content'], "is_user": False}
                ])

                for i, msg in enumerate(st.session_state.get('messages', [])):
                    is_user = msg["is_user"]
                    content = msg["content"]
                    if is_user:
                        message(f"You: {content}", is_user=True, key=f"user_msg_{i}")
                    else:
                        message(f"Agent: {content}", is_user=False, key=f"agent_msg_{i}")

        except Empty:
            time.sleep(0.1)  # Sleep for 100ms to prevent busy-waiting
        except Exception as e:
            print(f"Error in message_listener: {str(e)}")

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
            message(f"You: {st.session_state.get('messages', [])[-1]['content']}", is_user=True, key=f"user_msg_0")

            message_queue = Queue()

            # Start a thread that listens for messages from the agent and updates the UI
            listener_thread = threading.Thread(target=message_listener, args=(message_queue,))
            listener_thread.start()

            agent = StreamlitAgent()
            agent.run(user_input, update_ui)  

    # Move the message display outside the form block
    with response_container:
        # Create Queue for communication        
        for i, msg in enumerate(st.session_state.get('messages', [])):
            is_user = msg["is_user"]
            content = msg["content"].replace("TERMINATE", "")

            if is_user:
                message(f"You: {content}", is_user=True, key=f"user_msg_{i}")
            else:
                message(f"Agent: {content}", is_user=False, key=f"agent_msg_{i}")



if __name__ == '__main__':
    main()
"""
Utility functions for UI components

"""
import os
import json
import autogen
import chainlit as cl
from agents.chroma_agent import ChromaAgent

async def save_logs(logs_filename: str):
    # Make sure the directory exists
    os.makedirs(os.path.dirname(logs_filename), exist_ok=True)

    # Now save the logs
    logs = autogen.ChatCompletion.logged_history
    with open(logs_filename, "w") as log_file:
        json.dump(logs, log_file, indent=4)

    return logs

async def setup_agents(temperature: float,
                        model: str,
                        output_folder: str):
    """Create Agent objects and set user session variables"""

    docs_path = 'data/docs'
    db_path = 'data/chromadb'
    collection_name = 'autogen-discord'

    agent = ChromaAgent(docs_path, db_path, collection_name, 
                        temperature=temperature, model=model)
                        

    # User Session Variables TODO: make this dynamic
    secondary_agent_name = agent.secondary_agent.name.replace("_", " ")
    user_proxy_name = agent.user_proxy.name.replace("_", " ")

    # Setting user session variables
    cl.user_session.set('agent', agent)
    cl.user_session.set(secondary_agent_name, agent.secondary_agent)
    cl.user_session.set(user_proxy_name, agent.user_proxy)    


async def setup_chat_settings():
    # Set up agent configuration
    settings = await cl.ChatSettings(
            [
                cl.input_widget.Select(
                    id="Model",
                    label="Model",
                    values=["gpt-3.5-turbo",  "gpt-4-1106-preview", "gpt-4"],
                    initial_index=2
                ),
                cl.input_widget.Slider(id="Temperature", label="Temperature (randomness)", initial=0.5, min=0, max=2, step=0.1),
            ]
    ).send()

    return settings

async def setup_avatars():
    """Function for avatar icons"""
    avatar_configurations = [
        {
            "name": "User",
            "url": "https://api.dicebear.com/7.x/thumbs/svg?seed=Callie&rotate=360&eyes=variant4W14&eyesColor=ffffff,000000",
        },
        {
            "name": "User Proxy",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
        },
        {
            "name": "Data Engineer",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
        },
        {
            "name": "chatbot",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Dusty&backgroundColor=ffb300",
        },
        {
            "name": "chatbot",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Dusty&backgroundColor=ffb300",
        },
        {
            "name": "Code output",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
        },
        {
            "name": "Assistant Agent",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
        },
    ]
    
    for avatar in avatar_configurations:
        await cl.Avatar(
            name=avatar["name"],
            url=avatar["url"],
        ).send()


########################## Message Handling Functions ########################################

async def handle_text_file(file_element):
    # Process text file
    pass

async def handle_image_file(file_element):
    # Process image file
    pass

async def handle_message_indentation(naming_dict):
    agent = cl.user_session.get("agent")
    assistant = cl.user_session.get(agent.secondary_agent.name.replace("_", " "))
    user_proxy = cl.user_session.get(agent.user_proxy.name.replace("_", " "))
    final_response = None

    # Retrieve and filter message history
    original_message_history = assistant.chat_messages[user_proxy]
    last_seen_message_index = cl.user_session.get('last_seen_message_index', 0)
    new_message_history = original_message_history[last_seen_message_index+1:]
    
    termination_msgs = ["TERMINATE", "TERMINATE."]

    for i, message in enumerate(new_message_history):
        content = message.get("content", "").strip()
        function_call = message.get("function_call", "")
        content = content.replace("TERMINATE.", "").replace("TERMINATE", "").strip()

        # Skip empty messages
        if not content and not function_call:
            continue

        # Handle TERMINATE condition
        if "TERMINATE" in content:
            # content = content.replace("TERMINATE.", "").replace("TERMINATE", "").strip()
            # If the content is only "TERMINATE" or becomes empty after stripping, use the previous message
            if content == "" and i > 0:
                final_response = new_message_history[i - 1].get("content", "").strip()
                final_response = final_response.replace("TERMINATE.", "").replace("TERMINATE", "").strip()
                break
            elif content != "":
                final_response = content
                break
        else:
            final_response = content

        # Send non-empty messages
        if content:
            await cl.Message(
                author=naming_dict[message["role"]],
                content=content,
                indent=1
            ).send()
        
        if function_call:
            await cl.Message(
                author=naming_dict[message["role"]],
                content=function_call,
                indent=1
            ).send()

        # TODO: For each message:
        # If Terminate in content
        #   1. Check content.strip "TERMINATE" == exactly, if so then skip and don't set final message
        #   2. Check content.strip == "", if so then skip and don't set final message
        #   3. If step 1 or 2 are true then set the the message previous as the final message
        #       4. Apply same check as step 1: it shouldn't just be "TERMINATE". It should also not be an empty string
        #   5. If content contains other text, not just "TERMINATE", then "TERMINATE" or "TERMINATE."should
        #   6. `cl.Message()` should be used with content at each iteration with indent level 1


        # Check for TERMINATE condition
        # if "TERMINATE" in content:
        #     # If TERMINATE is the exact content of the last message, disregard it
        #     if content == "TERMINATE" and i == len(new_message_history) - 1:
        #         if i > 0:  # Ensure there is a message before the TERMINATE message
        #             final_response = new_message_history[i - 1].get("content", "").strip()
        #         break  # Stop processing as we've reached the end
        #     else:
        #         content = content.strip().replace("TERMINATE.", "").replace("TERMINATE", "").strip()  # Strip TERMINATE from the content

        # Check for TERMINATE condition
        # if "TERMINATE" in content:
        #     # Handle cases where TERMINATE is combined with other content
        #     if content != "TERMINATE":
        #         final_response = content.replace("TERMINATE", "").strip()
        #         break

        #     # If TERMINATE is the exact content of the last message, disregard it
        #     if i == len(new_message_history) - 1 and i > 0:
        #         final_response = new_message_history[i - 1].get("content", "").strip()
        #         break

            # Only send non-empty and non-TERMINATE contents
        #     await cl.Message(
        #         author=naming_dict[message["role"]],
        #         content=content,
        #         indent=1
        #     ).send()
        
        # if function_call:
        #     await cl.Message(
        #         author=naming_dict[message["role"]],
        #         content=function_call,
        #         indent=1
        #     ).send()

    cl.user_session.set('last_seen_message_index', len(original_message_history))
    if final_response is not None:
        final_response = final_response.strip().replace("TERMINATE.", "").replace("TERMINATE", "")
    print(final_response)
    return final_response



def update_cost_counter(logs):
    # Display cost logs and update total cost
    conversation = next(iter(logs.values()))
    cost = sum(conversation["cost"])
    TOTAL_COST = cl.user_session.get("total_cost", 0.0) + cost
    cl.user_session.set("total_cost", TOTAL_COST)

    # Display cost counter
    cost_counter = cl.TaskList(status="Done")
    cost_task = cl.Task(title=f"Total Cost in USD for this conversation: ${TOTAL_COST:.2f}", status=cl.TaskStatus.DONE)
    return cost_counter, cost_task


async def get_response(user_message: str):
    agent = cl.user_session.get("agent")
    assistant = cl.user_session.get(agent.secondary_agent.name.replace("_", " "))
    user_proxy = cl.user_session.get(agent.user_proxy.name.replace("_", " "))

    # Run the agent to get initial or continued response
    # TODO: Stream responses to UI
    if len(assistant.chat_messages[user_proxy]) == 0:
        print('initiating a conversation with agent.run()')
        await cl.make_async(agent.run)(prompt=user_message)
    else:
        print('continuing a conversation with agent._continue()')
        await cl.make_async(agent._continue)(prompt=user_message)


async def send_final_response(final_response):
            # Send the final message
    if final_response:
        await cl.Message(
            author="chatbot",
            content=final_response,
            indent=0
        ).send()

        chart_fig = None  # Get the chart figure
        if chart_fig:
            pass # TODO: Make code for displaying plotly dynamically in UI
    else:
        await cl.Message(
            author="chatbot",
            content="Sorry, please try again. we got lost in thought...",
            indent=0
        ).send()
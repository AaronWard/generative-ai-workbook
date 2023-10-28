import os
import sys
import json
import yaml
import openai
import shutil
import random
import autogen
# import tempfile
# import chromadb
# import evaluate
import pandas as pd
from typing import Any
from pathlib import Path

import wandb
import autogen
from autogen import AssistantAgent, UserProxyAgent

from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import QAGenerationChain
from langchain.evaluation.qa import QAEvalChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.callbacks import get_openai_callback
from langchain.output_parsers import OutputFixingParser
from langchain.output_parsers import PydanticOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings

from utils import is_termination_message

PROJECT_NAME = "wandb-autogen"
DOC_FILE = "documents/2308.08155.pdf"


# Helper functions
def get_split_docs(doc_file):
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=2000,
        chunk_overlap=100,
        length_function=len,
    )

    loader = PyPDFLoader(doc_file)
    pages = loader.load_and_split(text_splitter=text_splitter)
    return pages


def save_autogen_logs(logs_filename):
    logs = autogen.ChatCompletion.logged_history
    json.dump(logs, open(logs_filename, "w"),
              indent=4)
    return logs

def load_sweep_config(filename="config.yaml"):
    with open(filename, 'r') as file:
        sweep_configuration = yaml.safe_load(file)
    return sweep_configuration

def load_sweep_config():
    with open("config.yaml", 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(e)

def get_config(model_type):
    config_list = autogen.config_list_from_dotenv(
        dotenv_file_path="../../.env",
        model_api_key_map={
            "gpt-4": "OPENAI_API_KEY",
            "gpt-3.5-turbo": "OPENAI_API_KEY",
        },
        filter_dict={
            "model": {
                model_type,
            }
        }
    )
    return config_list


def get_random_chunks(num_qa_pairs):
    random_chunks = []
    for i in range(num_qa_pairs):
        random_chunks.append(random.randint(5, 172))  # (5, 172)

    return random_chunks


# LLM Functions
def instiate_agents(config_list, temperature):


    if os.path.exists('.cache') and os.path.isdir('.cache'):
        print('Deleting cache...')
        shutil.rmtree('.cache')

    if os.path.exists('.coding') and os.path.isdir('.coding'):
        print('Deleting previous work...')
        shutil.rmtree('.coding')


    coding_assistant_config = {
        "name": "coding_assistant",
        "llm_config": {
                "request_timeout": 1000,
                "seed": 42,
                "config_list": config_list,
                "temperature": temperature,
        }
    }
    coding_runner_config = {
        "name": "coding_runner",
        "human_input_mode": "NEVER",
        "max_consecutive_auto_reply": 5,
        "is_termination_msg": is_termination_message,
        "code_execution_config": {
                "work_dir": "./output",
                "use_docker": False
        },
        "llm_config": {
            "request_timeout": 1000,
            "seed": 42,
            "config_list": config_list,
            "temperature": temperature,
        },
    }

    coding_assistant = AssistantAgent(**coding_assistant_config)
    user_proxy = UserProxyAgent(**coding_runner_config)

    return coding_assistant, user_proxy


def get_qa_response(user_proxy,
                    assistant,
                    user_message,
                    config_list,
                    logs_filename):
    """ Function for getting answer from agents"""

    user_proxy.initiate_chat(
        assistant, message=user_message, config_list=config_list)
    logs = save_autogen_logs(logs_filename)

    conversation = next(iter(logs.values()))
    cost = sum(conversation["cost"])

    # Filter and modify messages with "TERMINATE" and take last message
    original_message_history = assistant.chat_messages[user_proxy]

    message_history = []
    for message in original_message_history:
        stripped_content = message["content"].strip()
        if stripped_content != "TERMINATE":
            if stripped_content.endswith("TERMINATE"):
                message["content"] = stripped_content.replace(
                    "TERMINATE", "").strip()
            message_history.append(message)

    if message_history:
        # Identify the final response
        return message_history[-1]["content"], cost
    else:
        return "No valid messages found.", cost


def get_eval_score(graded_outputs):
    """
    https://rajpurkar.github.io/SQuAD-explorer/

    Exact Match: For each question-answer pair, if the tokens of the model's prediction 
        exactly match the tokens of the true answer, exact_match is 100; otherwise, exact_match is 0. 
        One can imagine that each token matching is a rare occurrence for a stochastic system. 
        This metric should be taken with a grain of salt for our use case. 
    F1 Score: This is a well-known metric that cares equally about the precision and 
        recall of the system. Precision is the ratio of shared tokens to the total number of tokens 
        in the prediction. Recall is the ratio of shared tokens to the 
        total number of tokens in the ground truth.
    """

    correct = 0
    for graded_output in graded_outputs:
        assert isinstance(graded_output, dict)
        if graded_output["text"].strip() == "CORRECT":
            correct += 1

    return correct/len(graded_outputs)


def generate_eval_dataset(text):
    template = """You are a smart assistant designed to come up with meaninful question and answer pair. The question should be to the point and the answer should be as detailed as possible.
    Given a piece of text, you must come up with a question and answer pair that can be used to evaluate a QA bot. Do not make up stuff. Stick to the text to come up with the question and answer pair.
    When coming up with this question/answer pair, you must respond in the following format:
    ```
    {{
        "question": "$YOUR_QUESTION_HERE",
        "answer": "$THE_ANSWER_HERE"
    }}
    ```

    Everything between the ``` must be valid json.

    Please come up with a question/answer pair, in the specified JSON format, for the following text:
    ----------------
    {text}
    """

    prompt = PromptTemplate.from_template(template)

    # Generate QA
    llm = ChatOpenAI(temperature=0.9)
    return QAGenerationChain.from_llm(llm=llm, prompt=prompt).run()


def objective(config, qa_pairs, autogen_logs_filename):
    """
    Define the objective function to optimize.
    Computes a metric based on the provided configuration.
    
    Parameters:
    - config (Any): Configuration parameters for the model
    
    Returns:
    - 
    """
    model_type = config['parameters']['llm']
    temperature = config['additional_params']['temperature']


    # Set up Agent
    config_list = get_config(model_type)
    assistant, user_proxy = instiate_agents(model_type, temperature)
    predictions = []
    costs = []

    for qa_pair in qa_pairs:
        question = qa_pair["question"]
        print(question)
        response, cost = get_qa_response(user_proxy, 
                        assistant, 
                        question, 
                        config_list,
                        autogen_logs_filename)
        costs.append(float(cost))
        predictions.append({"response": response })

   
    # Evaluation 
    eval_chain = QAEvalChain.from_llm(llm = OpenAI(temperature=0))

    graded_outputs = eval_chain.evaluate(
        qa_pairs, predictions, question_key="question", prediction_key="response"
    )

    score = get_eval_score(graded_outputs)

    # Some data munging to get the examples in the right format
    for i, eg in enumerate(qa_pairs):
        eg["id"] = str(i)
        eg["answers"] = {"text": [eg["answer"]], "answer_start": [0]}
        predictions[i]["id"] = str(i)
        predictions[i]["prediction_text"] = predictions[i]["response"]

    for p in predictions:
        del p["response"]

    new_qa_pairs = qa_pairs.copy()
    for eg in new_qa_pairs:
        del eg["question"]
        del eg["answer"]

    
    return score, new_qa_pairs, costs

def main():
    """
    Main function to initialize wandb and log the results.
    """
    # Initialize W&B run
    run = wandb.init(project=PROJECT_NAME, config=sweep_configuration)
    random_chunks = get_random_chunks(wandb.config.num_qa_pairs)
    
    # Filenames
    autogen_logs_filename=f"logs_filename_{wandb.run.name}" # TODO: Where to find sweep_id in the config?

    # Generate evaluation dataset
    pages = get_split_docs(DOC_FILE)
    qa_pairs = []
    for idx in random_chunks:
        qa = generate_eval_dataset(pages[idx].page_content)
        qa_pairs.extend(qa)

    # log questions
    qa_df = pd.DataFrame(qa_pairs)
    run.log({"QA Eval Pair": qa_df})

    # Get the score from the objective function
    score, new_qa_pairs, costs = objective(wandb.config, qa_pairs, autogen_logs_filename)
    # visualize_results(wandb.config)
    cost = round(sum(costs), 2)

    # Log the score to W&B
    run.log({"score": score, 
             "new_qa_pairs": new_qa_pairs,
             "cost": cost})

    run.finish()

if __name__ == "__main__":
    print('Starting initiation...')
    sweep_configuration = load_sweep_config()
    sweep_id = wandb.sweep(sweep=sweep_configuration, project=PROJECT_NAME)
    wandb.agent(sweep_id, function=main, count=5)
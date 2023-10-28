"""
Script for evaluating how well autogen agents
can carry out tasks given different hyperparameters

to kill the process:
>  pkill wandb-service

"""
import os
import sys
import json
import yaml
import openai
import shutil
import random
import autogen
import pandas as pd
from typing import Any
from pathlib import Path

import wandb
import autogen
from dotenv import load_dotenv
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

load_dotenv()

PROJECT_NAME = "wandb-autogen"
DOC_FILE = "documents/2308.08155.pdf"

# api = wandb.Api()

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

def get_random_chunks(num_qa_pairs, max_index):
    return random.sample(range(5, max_index + 1), num_qa_pairs)

# LLM Functions
def instiate_agents(config_list, temperature):
    if os.path.exists('.cache') and os.path.isdir('.cache'):
        print('Deleting cache...')
        shutil.rmtree('.cache')

    if os.path.exists('.coding') and os.path.isdir('.coding'):
        print('Deleting previous work...')
        shutil.rmtree('.coding')


    assistant_config = {
        "name": "coding_assistant",
        "system_message": "You are an intelligent assistant chatbot that replies with the correct answer. Reply `TERMINATE` in the end when everything is done.",
        "llm_config": {
                "request_timeout": 1000,
                "seed": 42,
                "config_list": config_list,
                "temperature": temperature,
        }
    }
    proxy_config = {
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

    coding_assistant = AssistantAgent(**assistant_config)
    user_proxy = UserProxyAgent(**proxy_config)

    return coding_assistant, user_proxy


def get_qa_response(model_type,
                    user_proxy,
                    assistant,
                    user_message,
                    config_list,
                    logs_filename):
    """ Function for getting answer from agents"""

    if model_type == "gpt-3.5-turbo":
        termination_notice = (
            '\n\nDo not show appreciation in your responses, say only what is necessary. '
            'if "Thank you" or "You\'re welcome" are said in the conversation, then say TERMINATE '
            'to indicate the conversation is finished and this is your last message.'
        )

        user_message += termination_notice

    autogen.ChatCompletion.start_logging()
    user_proxy.initiate_chat(assistant, message=user_message, config_list=config_list, silent=False)
    logs = autogen.ChatCompletion.logged_history
    autogen.ChatCompletion.stop_logging()

    json.dump(logs, open(logs_filename, "w"), indent=4)

    # logs = save_autogen_logs(logs_filename)
    if logs:
        conversation = next(iter(logs.values()))
        cost = sum(conversation["cost"])
    else:
        raise ValueError("Logs are none.")

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
        if graded_output["results"].strip() == "CORRECT":
            correct += 1

    return correct/len(graded_outputs)


def get_data_generator():
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
    chain = QAGenerationChain.from_llm(llm=llm, prompt=prompt)

    return chain


def objective(config, qa_pairs, autogen_logs_filename):
    """
    Define the objective function to optimize.
    Computes a metric based on the provided configuration.
    
    Parameters:
    - config (Any): Configuration parameters for the model
    
    Returns:
    - 
    """
    model_type = config.llm
    temperature = config.temperature

    # Set up Agent
    config_list = get_config(model_type)
    assistant, user_proxy = instiate_agents(config_list, temperature)
    predictions = []
    costs = []

    for qa_pair in qa_pairs:
        question = qa_pair["question"]
        print(question)
        response, cost = get_qa_response(model_type,
                                        user_proxy, 
                                        assistant, 
                                        question, 
                                        config_list,
                                        autogen_logs_filename)
        costs.append(float(cost))
        predictions.append({"response": response})
   
    # Evaluation 
    eval_chain = QAEvalChain.from_llm(llm = OpenAI(temperature=0))

    graded_outputs = eval_chain.evaluate(
        qa_pairs, predictions, question_key="question", prediction_key="response"
    )

    print(graded_outputs)

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

def main(config=None):
    """
    Main function to initialize wandb and log the results.

    """

    with wandb.init(project=PROJECT_NAME, config=config) as run:
        print(wandb.config)
        config = wandb.config
        autogen_logs_filename=f"logs_filename_{run.name}"
        print(autogen_logs_filename)
        print(config)

        # Get the score from the objective function
        score, new_qa_pairs, costs = objective(config, qa_pairs, autogen_logs_filename)
        cost = round(sum(costs), 2)

        args = {
                "score": score, 
                "num_questions": len(new_qa_pairs),
                "cost": cost
        }
        config.update(args)

        # Log the score to W&B
        run.log(config)


if __name__ == "__main__":
    import pprint as pp
    print('Starting initiation...')

    sweep_configuration = load_sweep_config()
    gen_chain = get_data_generator()

    # Generate evaluation dataset
    pages = get_split_docs(DOC_FILE)
    random_chunks = get_random_chunks(num_qa_pairs=5, max_index=len(pages) - 1)

    qa_pairs = []
    for idx in random_chunks:
        response = gen_chain.run(pages[idx].page_content)
        qa_pairs.extend(response)

    qa_df = pd.DataFrame(qa_pairs)
    pp.pprint(qa_df)
    print()

    sweep_id = wandb.sweep(sweep=sweep_configuration, project=PROJECT_NAME)
    wandb.agent(sweep_id, function=main, count=5)
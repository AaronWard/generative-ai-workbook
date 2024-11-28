"""
# main.py

The following script will analyze a list of youtube channels
The video transcript is summarized and then categorized into 
topics using ControlFlow agents. 
"""
import os
import re
import json
from typing import List
from datetime import datetime, timedelta

from dotenv import load_dotenv
import controlflow as cf
from pydantic import BaseModel
# from langchain_ollama import ChatOllama
# from langchain_experimental.llms.ollama_functions import OllamaFunctions

load_dotenv()

from utils.youtube_utils import fetch_transcript, fetch_videos_from_channel, download_channel_icon
from utils.file_utils import load_prompt
class CategorizationResult(BaseModel):
    categories: List[str]

def load_topics():
    return [
        "In-context learning",
        "Multimodal models", 
        "Agents",
        "Vector Databases",
        "Prompting",
        "Chain of thought reasoning",
        "Image",
        "Search", 
        "Classification",
        "Topic Modelling",
        "Clustering",
        "Data, Text and Code generation",
        "Summarization",
        "Rewriting",
        "Extractions", 
        "Proof reading",
        "Swarms",
        "Querying Data",
        "Framework or Library",
        "Fine tuning",
        "Executing code",
        "Sentiment Analysis",
        "Planning and Complex Reasoning",
        "Image classification and generation (If multi-modal)",
        "Philosophical reasoning and ethics",
        "Reinforcement learning",
        "Model security and privacy",
        "APIs",
        "Infrastructure"
    ]


@cf.flow
def main():
    """
    Main function to analyze a list of youtube channels
    
    
    NOTE: Having issues with summarization using ollama models for some reason.Using OpenAI for now.
    https://linen.prefect.io/t/23129868/hi-everyone-i-have-a-question-can-we-integrate-controlflow-w
    https://github.com/PrefectHQ/ControlFlow/discussions/379
    """
    TOPICS = load_topics()
    n_days = 365
    os.makedirs('./ui/src/data', exist_ok=True)  # Ensure data is saved in ui/src/data
    
    # model_name = 'llama3.1:8b'  # Ensure the provider is not specified
    # model = ChatOllama(model=model_name, 
    #                    stream=True)
    model = "openai/gpt-4o-mini"  

    summary_agent = cf.Agent(
        name="Video Transcript Summarization Agent",
        description="Expert in summarizing YouTube video transcripts to capture the main nuggets of information.",
        model=model,
    )

    categorize_agent = cf.Agent(
        name="Topic Categorization Agent",
        description="Expert in quickly categorizing topics from a description of a video",
        model=model,
    )
    
    max_date = datetime.now() - timedelta(days=n_days)
    channel_urls = [
        # "https://www.youtube.com/@AIJasonZ/videos",
        # "https://www.youtube.com/@indydevdan/videos",
        # "https://www.youtube.com/@vrsen/videos",
        # "https://www.youtube.com/@matthew_berman/videos",
        # "https://www.youtube.com/@YannicKilcher/videos",
        # "https://www.youtube.com/@jamesbriggs/videos",
        # "https://www.youtube.com/@WesRoth/videos", 
        # "https://www.youtube.com/@aiexplained-official/videos",
        # "https://www.youtube.com/@alejandro_ao/videos",
        # "https://www.youtube.com/@AllAboutAI/videos",
        # "https://www.youtube.com/@AssemblyAI/videos", 
        # "https://www.youtube.com/@DaveShap/videos",
        # "https://www.youtube.com/@EdanMeyer/videos",
        # "https://www.youtube.com/@mreflow/videos",
        # "https://www.youtube.com/@maya-akim/videos",
        # "https://www.youtube.com/@MervinPraison/videos",
        # "https://www.youtube.com/@ShawhinTalebi/videos",
        "https://www.youtube.com/@1littlecoder/videos",
        # "https://www.youtube.com/@YaronBeen/videos"
        "https://www.youtube.com/@ColeMedin/videos"
        # "https://www.youtube.com/@Tunadorable/videos"
    ]

    for channel_url in channel_urls:
        videos = fetch_videos_from_channel(channel_url, max_date)
        if not videos:
            print(f"No recent videos found for channel: {channel_url}")
            continue

        # Use the first video's channel info (since it's the same for all videos)
        channel_name = videos[0]['channel_title']
        channel_icon_url = videos[0]['channel_icon_url']

        # Download the channel icon
        channel_icon_path = download_channel_icon(channel_name, channel_icon_url)

        print(f"\n\nProcessing channel: {channel_name} with a total of {len(videos)} videos in the past {n_days} days\n\n")

        for video in videos:
            print(f"\n\nProcessing video: {video['title']}\n\n")

            transcript = fetch_transcript(video['video_id'])
            description = video.get('description', '')
            title = video.get('title', '')

            # Skip the video if both transcript and description are missing
            if not title and not transcript and not description:
                print(f"No title, transcript, or description available for video ID: {video['video_id']}")
                continue  # Skip to the next video

            # Run the process_video_flow for the current video
            video_result = process_video_flow(
                    transcript,
                    description,
                    title,
                    TOPICS,
                    summary_agent,
                    categorize_agent,
                    channel_name,
                    channel_icon_path,
                    video.get('published_at', ''),
                    f"https://www.youtube.com/watch?v={video['video_id']}"
                )

            # Load existing data if the file exists
            sanitized_channel_name = re.sub(r'\W+', '', channel_name)
            file_path = f'./ui/src/data/{sanitized_channel_name}.json'
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as json_file:
                        existing_data = json.load(json_file)
                except json.JSONDecodeError:
                    existing_data = []
            else:
                existing_data = []

            # Append new result to existing data
            existing_data.append(video_result)

            # Save updated data back to the JSON file
            with open(file_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)

    print("Done!")


def process_video_flow(transcript, description, title, TOPICS, summary_agent, categorize_agent, channel_name, channel_icon_path, published_at, video_url):
    transcript_text = transcript.strip() if transcript else ''
    description_text = description.strip() if description else ''
    title_text = title.strip() if title else ''

    # Skip if all are empty
    if not title_text and not description_text and not transcript_text:
        print(f"No content available to summarize for video '{video_url}'. Skipping.")
        return None  # Return None to indicate skipping this video

    # Task 1: Summarize Video Description
    def summarize_video():
        summary_prompt = load_prompt(
            'prompts/summarize.txt',
            title=title_text,
            description=description_text,
            transcript=transcript_text
        )
        summary_result = cf.run(
            objective="Summarize the video to capture main insights",
            instructions=summary_prompt,
            agents=[summary_agent]
        )        
        return summary_result

    summary_result = summarize_video()
    if not summary_result:
        print(f"Failed to generate summary for video '{title_text}'. Skipping.")
        return None  # Return None to indicate skipping this video

    # Task 2: Categorize Video based on summary
    def categorize_video():
        if not summary_result or summary_result == "No summary available.":
            print(f"No valid summary available for categorization for video '{title_text}'.")
            return None
        
        categorize_prompt = load_prompt(
            'prompts/categorize.txt',
            predefined_topics=TOPICS,
            summary=summary_result
        )
        categories_output = cf.run(
            objective="Categorize the video summary into predefined topics",
            instructions=categorize_prompt,
            result_type=CategorizationResult,
            agents=[categorize_agent]
        )
        categories_result = categories_output.categories
        return categories_result

    categories_result = categorize_video()
    if categories_result is None:
        print(f"Skipping video '{title_text}' due to failure in categorization.")
        return None   # Return None to indicate skipping this video

    # Collect the results
    video_result = {
        'channel': channel_name,
        'channelIcon': channel_icon_path,
        'title': title_text,
        'description': description_text,
        'summary': summary_result,
        'categories': categories_result,
        'url': video_url,
        'published_at': published_at
    }
    return video_result

if __name__ == "__main__":
    main()
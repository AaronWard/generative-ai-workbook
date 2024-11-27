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

load_dotenv()

from utils.youtube_utils import fetch_transcript, fetch_videos_from_channel
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
    TOPICS = load_topics()
    n_days = 365
    
    # Ensure the data directory exists
    os.makedirs('./data', exist_ok=True)
    
    summary_agent = cf.Agent(
        name="Video Transcript Summarization Agent",
        description="Expert in summarizing youtube video transcripts to capture the main nuggets of information.",
        model="openai/gpt-4o",
    )

    categorize_agent = cf.Agent(
        name="Topic Categorization Agent",
        description="Expert in quickly categorizing topics from a description of a video",
        model="openai/gpt-4o",
    )

    max_date = datetime.now() - timedelta(days=n_days)
    channel_urls = [
        # "https://www.youtube.com/@vrsen/videos",
        "https://www.youtube.com/@indydevdan/videos",
        "https://www.youtube.com/@AIJasonZ/videos",
    ]

    for channel_url in channel_urls:
        videos = fetch_videos_from_channel(channel_url, max_date)
        # Extract channel name from URL
        channel_name = channel_url.split('@')[1].split('/')[0]
        print(f"\n\nProcessing channel: {channel_name} with a total of {len(videos)} videos in the past {n_days} days\n\n")
        
        for video in videos:
            print(f"\n\nProcessing video: {video['title']}\n\n")

            transcript = fetch_transcript(video['video_id'])
            description = video.get('description', '')

            # Fallback logic
            if not transcript and not description:
                print(f"No transcript or description available for video ID: {video['video_id']}")
                continue  # Skip to the next video

            if transcript and description:
                content = f"{transcript}\n\nVideo Description:\n{description}"
            elif transcript:
                content = transcript
            elif description:
                content = description
            else:
                print(f"No transcript or description available for video ID: {video['video_id']}")
                continue

            # Create a flow for processing each video
            @cf.flow(context_kwargs=["content", "TOPICS"])
            def process_video_flow(content, TOPICS):
                # Task 1: Summarize Video Description
                def summarize_video():
                    summary_prompt = load_prompt('prompts/summarize.txt', title=video['title'], description=video['description'], transcript=content)
                    summary_result = cf.run(
                        objective="Summarize the video transcript to capture main insights",
                        instructions=summary_prompt,
                        agents=[summary_agent]
                    )

                    return summary_result

                summary_result = summarize_video()

                # Task 2: Categorize Video based on summary
                def categorize_video():
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

                # Collect the results
                video_result = {
                    'channel': channel_name,
                    'title': video['title'],
                    'description': video['description'],
                    'summary': summary_result,
                    'categories': categories_result,
                    'url': f"https://www.youtube.com/watch?v={video['video_id']}",
                    'published_at': video['published_at']
                }
                return video_result

            # Run the process_video_flow for the current video
            video_result = process_video_flow(content, TOPICS)

            # Load existing data if the file exists
            file_path = f'./data/{channel_name}.json'
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

if __name__ == "__main__":
    main()
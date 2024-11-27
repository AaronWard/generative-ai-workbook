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
from googleapiclient.discovery import build

load_dotenv()

from utils.transcript_utils import fetch_transcript
class CategorizationResult(BaseModel):
    categories: List[str]


def load_topics(file_path='topics_updated.txt'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    else:
        return [
            "In context learning",
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

def resolve_channel_id_from_handle(youtube, handle):
    response = youtube.search().list(
        part='snippet',
        q=handle,
        type='channel',
        maxResults=1
    ).execute()

    if response['items']:
        return response['items'][0]['id']['channelId']
    else:
        raise ValueError("Could not resolve handle to a channel ID")

def extract_channel_id(channel_url):
    # Check for different URL patterns
    if "youtube.com/channel/" in channel_url:
        match = re.search(r"youtube\.com/channel/([^/?]+)", channel_url)
    elif "youtube.com/user/" in channel_url:
        match = re.search(r"youtube\.com/user/([^/?]+)", channel_url)
    elif "youtube.com/c/" in channel_url or "youtube.com/@" in channel_url:
        # For custom URLs or handles, you might need to resolve them using the API
        # This is a placeholder for additional logic
        raise NotImplementedError("Custom URLs or handles need additional logic to resolve to channel IDs.")
    else:
        raise ValueError("Invalid channel URL format")

    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid channel URL format")

def fetch_videos_from_channel(channel_url, max_date):
    api_key = os.getenv('YOUTUBE_API_KEY')
    youtube = build('youtube', 'v3', developerKey=api_key)

    if "youtube.com/@" in channel_url:
        handle = channel_url.split('@')[1].split('/')[0]
        channel_id = resolve_channel_id_from_handle(youtube, handle)
    else:
        channel_id = extract_channel_id(channel_url)

    # Fetch uploads playlist ID
    response = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    
    uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Fetch videos from the uploads playlist
    videos = []
    next_page_token = None
    while True:
        playlist_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        
        for item in playlist_response['items']:
            video_published_at = item['snippet']['publishedAt']
            video_date = datetime.strptime(video_published_at, '%Y-%m-%dT%H:%M:%SZ')
            if video_date < max_date:
                continue

            videos.append({
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'video_id': item['snippet']['resourceId']['videoId'],
                'published_at': video_published_at
            })
        
        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    return videos

def load_prompt(file_path, **kwargs):
    with open(file_path, 'r') as file:
        prompt_template = file.read()
    for key, value in kwargs.items():
        if isinstance(value, list):
            formatted_list = '\n'.join(value)
            kwargs[key] = formatted_list
    return prompt_template.format(**kwargs)

@cf.flow
def main():
    TOPICS = load_topics()
    
    summary_agent = cf.Agent(
        name="Video Transcript Summarization Agent",
        description="Expert in summarizing youtube video transcripts to capture the main nuggets of information.",
    )

    categorize_agent = cf.Agent(
        name="Topic Categorization Agent",
        description="Expert in quickly categorizing topics from a description of a video",
    )

    max_date = datetime.now() - timedelta(days=365)
    channel_urls = [
        "https://www.youtube.com/@vrsen/videos",
        # ... (other channels)
    ]
    all_results = []

    for channel_url in channel_urls:
        videos = fetch_videos_from_channel(channel_url, max_date)
        for video in videos:
            print(video)
            transcript = fetch_transcript(video['video_id'])
            description = video.get('description', '')

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
                    summary_prompt = load_prompt('prompts/summarize2.txt', transcript=content)
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
                        'prompts/categorize2.txt',
                        summary=summary_result,
                        predefined_topics=TOPICS
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

                # Append any new topics to TOPICS
                for category in categories_result:
                    if category not in TOPICS:
                        TOPICS.append(category)

                # Collect the results
                video_result = {
                    'title': video['title'],
                    'summary': summary_result,
                    'categories': categories_result,
                    'url': f"https://www.youtube.com/watch?v={video['video_id']}",
                    'published_at': video['published_at']
                }
                return video_result

            # Run the process_video_flow for the current video
            video_result = process_video_flow(content, TOPICS)
            all_results.append(video_result)

        # Extract channel name from URL
        channel_name = channel_url.split('@')[1].split('/')[0]

        # Ensure the data directory exists
        os.makedirs('./data', exist_ok=True)

        # Save results to a JSON file named after the channel
        with open(f'./data/{channel_name}.json', 'w') as json_file:
            json.dump(all_results, json_file, indent=4)

    # Output results
    for result in all_results:
        print(f"Title: {result['title']}")
        print(f"Summary: {result['summary']}")
        print(f"Categories: {result['categories']}")
        print(f"URL: {result['url']}")
        print(f"Published at: {result['published_at']}\n")

    # Optionally, save the updated TOPICS list
    with open('topics_updated.txt', 'w') as f:
        for topic in TOPICS:
            f.write(f"{topic}\n")

if __name__ == "__main__":
    main()
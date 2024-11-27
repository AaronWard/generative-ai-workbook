import os
import re
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

def fetch_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])
        transcript_data = transcript.fetch()
        full_text = ' '.join([item['text'] for item in transcript_data])
        return full_text
    except Exception as e:
        print(f"Could not retrieve transcript for video {video_id}: {e}")
        return None

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

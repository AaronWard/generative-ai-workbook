import os
import re
import requests
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
    

def download_channel_icon(channel_name, channel_icon_url):
    # Ensure the icons directory exists
    icons_dir = './ui/public/assets/icons'
    os.makedirs(icons_dir, exist_ok=True)

    # Define the path where the icon will be saved
    # Use channel_name in the filename to ensure uniqueness
    sanitized_channel_name = re.sub(r'\W+', '', channel_name)  # Remove non-alphanumeric characters
    icon_filename = f"{sanitized_channel_name}.jpg"
    icon_path = os.path.join(icons_dir, icon_filename)

    # Download the image only if it doesn't already exist
    if not os.path.exists(icon_path):
        try:
            response = requests.get(channel_icon_url, stream=True)
            if response.status_code == 200:
                with open(icon_path, 'wb') as out_file:
                    for chunk in response.iter_content(1024):
                        out_file.write(chunk)
                print(f"Downloaded icon for channel {channel_name}")
            else:
                print(f"Failed to download icon for channel {channel_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Error downloading icon for channel {channel_name}: {e}")
    else:
        print(f"Icon for channel {channel_name} already exists. Skipping download.")

    # Return the relative path to the icon for use in JSON data
    return f"/assets/icons/{icon_filename}"

    

def fetch_videos_from_channel(channel_url, max_date):
    api_key = os.getenv('YOUTUBE_API_KEY')
    youtube = build('youtube', 'v3', developerKey=api_key)

    if "youtube.com/@" in channel_url:
        handle = channel_url.split('@')[1].split('/')[0]
        channel_id = resolve_channel_id_from_handle(youtube, handle)
    else:
        channel_id = extract_channel_id(channel_url)

    # Fetch channel details including snippet to get thumbnails
    channel_response = youtube.channels().list(
        part='snippet,contentDetails',
        id=channel_id
    ).execute()

    channel_snippet = channel_response['items'][0]['snippet']
    channel_title = channel_snippet['title']
    channel_thumbnails = channel_snippet.get('thumbnails', {})

    # Extract the highest resolution thumbnail available
    if 'maxres' in channel_thumbnails:
        channel_icon_url = channel_thumbnails['maxres']['url']
    elif 'high' in channel_thumbnails:
        channel_icon_url = channel_thumbnails['high']['url']
    else:
        channel_icon_url = channel_thumbnails.get('default', {}).get('url', '')

    # Fetch uploads playlist ID
    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

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
                'published_at': video_published_at,
                'channel_title': channel_title,
                'channel_icon_url': channel_icon_url  # Add channel icon URL here
            })
        
        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    return videos

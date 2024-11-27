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
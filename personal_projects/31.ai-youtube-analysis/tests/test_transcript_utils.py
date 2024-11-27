import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.transcript_utils import fetch_transcript

class TestTranscriptUtils(unittest.TestCase):

    def test_fetch_transcript_valid_video(self):
        # Replace 'VALID_VIDEO_ID' with a real video ID that has subtitles
        video_id = 'ujnLJru2LIs'
        transcript = fetch_transcript(video_id)
        self.assertIsNotNone(transcript)
        self.assertIsInstance(transcript, str)
        self.assertGreater(len(transcript), 0)

    def test_fetch_transcript_invalid_video(self):
        # Use an invalid video ID to test error handling
        video_id = 'invalid_video_id'
        transcript = fetch_transcript(video_id)
        self.assertIsNone(transcript)

if __name__ == '__main__':
    unittest.main()
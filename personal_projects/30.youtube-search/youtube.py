"""
This code is inspired by Echohive youtube tutorial 

"""

import os
import openai
import numpy as np
import tiktoken
from youtube_transcript_api import YouTubeTranscriptApi
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from typing import List, Dict

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path("../../.env"))

# Load OpenAI API key from environment variable
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
console = Console()


class YouTubeSearchApp:
    def __init__(self, model):
        """
        Initialize the YouTubeSearchApp with the specified embedding model.

        :param model: The OpenAI embedding model to use
        """
        # Dictionary to store transcripts for processed videos
        self.transcripts = {}
        # Dictionary to store embeddings for processed videos
        self.embeddings = {}
        # The embedding model we'll use
        self.model = model
        # Tokenizer for the chosen model
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def fetch_transcript(self, video_id: str) -> List[Dict]:
        """
        Fetches the transcript of a given YouTube video.

        :param video_id: The ID of the YouTube video
        :return: A list of dictionaries containing transcript data
        """
        try:
            # Use the YouTube Transcript API to get the transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception as e:
            # If there's an error, print it in red
            console.print(f"[red]Error fetching transcript: {str(e)}[/red]")
            return []

    def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generates embeddings for a list of texts using OpenAI’s Embeddings API.

        :param texts: A list of text strings to generate embeddings for
        :return: A list of numpy arrays representing the embeddings
        """
        try:
            # Use OpenAI's API to create embeddings for our texts
            response = client.embeddings.create(
                input=texts,
                model=self.model,
            )
            # Convert the embeddings to numpy arrays for easier manipulation
            embeddings = [np.array(data.embedding) for data in response.data]
            # print(embeddings)
            return embeddings
        except Exception as e:
            # If there's an error, print it in red
            console.print(f"[red]Error generating embeddings: {str(e)}[/red]")
            return []

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Computes the cosine similarity between two embeddings.

        :param a: First embedding vector
        :param b: Second embedding vector
        :return: Cosine similarity score
        """
        # Calculate the dot product of the two vectors
        # divided by the product of their magnitudes
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def process_video(self, video_id: str):
        """
        Fetches the transcript for a video, generates embeddings for each part, and stores them for similarity search.

        :param video_id: The ID of the YouTube video to process
        """
        # Get the transcript for the video
        transcript = self.fetch_transcript(video_id)
        if not transcript:
            print("[yellow]This video does not contain a transcript")
            return

        # Extract the text and timestamps from the transcript
        texts = [entry["text"] for entry in transcript]
        timestamps = [entry["start"] for entry in transcript]

        # Count the total number of tokens in the transcript
        total_tokens = sum(len(self.encoding.encode(text)) for text in texts)
        # Warn if the total tokens exceed the model's limit
        if total_tokens > 8191:
            console.print(
                f"[yellow]Warning: Total tokens ({total_tokens}) exceed model limit (8191). Some content may be truncated.[/yellow]"
            )

        # Generate embeddings for each piece of text in the transcript
        embeddings = self.generate_embeddings(texts)
        if not embeddings:
            return

        # Store the processed data for this video
        self.transcripts[video_id] = {
            "texts": texts,
            "timestamps": timestamps,
            "embeddings": embeddings,
        }

        console.print(f"[green]Processed video with ID: {video_id}[/green]")


    def search(self, video_id: str, query: str):
        """
        Searches for the most similar transcript segment in the video based on a user query.

        :param video_id: The ID of the YouTube video to search
        :param query: The user's search query
        """
        # Check if we have processed this video before
        if video_id not in self.transcripts:
            console.print(f"[red]No transcript found for video ID: {video_id}[/red]")
            return

        # Get the stored data for this video
        video_data = self.transcripts[video_id]

        # Generate an embedding for the user's query
        query_embedding = self.generate_embeddings([query])[0]

        # Calculate similarities between query and all transcript segments
        similarities = [
            self.cosine_similarity(query_embedding, embed)
            for embed in video_data["embeddings"]
        ]

        # Get the top 5 results, sorted by similarity
        top_indices = np.argsort(similarities)[-5:][::-1]

        # Create a rich table to display the results
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="dim", width=6)
        table.add_column("Similarity", justify="right")
        table.add_column("Timestamp", justify="center")
        table.add_column("Text", justify="left", width=60)
        table.add_column("Link", justify="center")

        # Add each of the top 5 results to the table
        for rank, idx in enumerate(top_indices):
            timestamp = video_data["timestamps"][idx]
            text = video_data["texts"][idx]
  
            similarity = similarities[idx]
            formatted_time = self.format_time(timestamp)
            youtube_link = f"https://www.youtube.com/watch?v={video_id}&t={int(timestamp)}"
            table.add_row(
                f"{rank + 1}",
                f"{similarity:.3f}",
                formatted_time,
                text,
                f"[link={youtube_link}]Click[/link]",
            )

        console.print(table)

    def format_time(self, seconds: float) -> str:
        """
        Formats the time from seconds into HH:MM:SS.

        :param seconds: Time in seconds
        :return: Formatted time string
        """
        # Convert seconds to hours, minutes, and seconds
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        # Return the formatted time string
        return f"{h:02}:{m:02}:{s:02}"


def run_app():
    """
    Main loop for the YouTube Search App. Handles input and interactions.
    """
    # Display options for embedding models
    console.print("[cyan]Choose an embedding model:[/cyan]")
    console.print(
        "1. text-embedding-3-small (Fastest, 62.3% MTEB performance, ~62,500 pages/dollar)"
    )
    console.print(
        "2. text-embedding-3-large (Most accurate, 64.6% MTEB performance, ~9,615 pages/dollar)"
    )
    console.print(
        "3. text-embedding-ada-002 (Legacy model, 61.0% MTEB performance, ~12,500 pages/dollar)"
    )

    # Ask the user to choose a model
    choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"])

    # Map the user's choice to the actual model name
    model_map = {
        "1": "text-embedding-3-small",
        "2": "text-embedding-3-large",
        "3": "text-embedding-ada-002",
    }
    model = model_map[choice]

    # Create an instance of our YouTubeSearchApp with the chosen model
    app = YouTubeSearchApp(model=model)
    console.print(f"[green]Using {model} for embeddings.[/green]")

    current_video_id = None

    # Main loop
    while True:
        if not current_video_id:
            # Ask the user for a YouTube URL
            console.print("[cyan]Enter a YouTube URL (or type 'exit' to quit):[/cyan]")
            url = Prompt.ask("YouTube URL")
            if url.lower() == "exit":
                break

            # Extract the video ID from the URL
            video_id = extract_video_id(url)
            if not video_id:
                console.print("[red]Invalid YouTube URL![/red]")
                continue

            # Process the video (fetch transcript and generate embeddings)
            app.process_video(video_id)
            current_video_id = video_id

        # Ask the user for a search query or new action
        console.print(
            f"[cyan]Enter your search query for the video (or 'new' for a new video, 'exit' to quit):[/cyan]"
        )
        query = Prompt.ask("Search Query")
        if not query:
            continue
        if query.lower() == "exit":
            break
        elif query.lower() == "new":
            current_video_id = None
            continue

        # Search the video transcript for the query
        app.search(current_video_id, query)


def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.

    :param url: YouTube URL
    :return: Video ID if found, None otherwise
    """
    import re

    # Regular expression to match YouTube video IDs
    video_id_regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(video_id_regex, url)
    if match:
        return match.group(1)
    else:
        return None


if __name__ == "__main__":
    # If this script is run directly, start the app
    run_app()

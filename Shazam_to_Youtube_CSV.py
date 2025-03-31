import os
import json
import pandas as pd
import time
from youtubesearchpython import VideosSearch
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# YouTube API configuration
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"


def authenticate_youtube():
    """Authenticate with YouTube API and return a service object."""
    credentials = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as token:
            token_info = json.load(token)
            try:
                from google.oauth2.credentials import Credentials
                credentials = Credentials.from_authorized_user_info(token_info)
            except Exception:
                print("Invalid token format. Re-authenticating...")

    if not credentials or not credentials.valid:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        credentials = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(credentials.to_json())

    return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def check_youtube_channel(youtube):
    """Check if the authenticated user has a valid YouTube channel."""
    try:
        request = youtube.channels().list(part="id", mine=True)
        response = request.execute()
        if "items" in response and response["items"]:
            print("✅ YouTube channel found:", response["items"][0]["id"])
            return True
        print("❌ No YouTube channel found. Please create one.")
    except googleapiclient.errors.HttpError as error:
        print(f"Error checking YouTube channel: {error}")
    return False


def get_existing_playlist(youtube, playlist_title):
    """Search for an existing YouTube playlist by title."""
    try:
        request = youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=10  # Limit the search to 10 playlists (you can increase if needed)
        )
        response = request.execute()
        playlists = response.get("items", [])
        for playlist in playlists:
            if playlist["snippet"]["title"].lower() == playlist_title.lower():
                print(f"✅ Found existing playlist: {playlist_title}")
                return playlist["id"]
        print(f"❌ No playlist found with the title: {playlist_title}")
    except googleapiclient.errors.HttpError as error:
        print(f"❌ Error searching for playlist: {error}")
    return None


def get_playlist_videos(youtube, playlist_id):
    """Retrieve all video titles from a YouTube playlist."""
    existing_videos = set()
    try:
        next_page_token = None
        while True:
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,  # Max allowed per request
                pageToken=next_page_token
            )
            response = request.execute()
            for item in response.get("items", []):
                video_title = item["snippet"]["title"].lower()
                existing_videos.add(video_title)
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        print(f"✅ Retrieved {len(existing_videos)} videos from playlist")
    except googleapiclient.errors.HttpError as error:
        print(f"❌ Error retrieving playlist videos: {error}")
    return existing_videos


def add_video_to_playlist(youtube, playlist_id, video_id):
    """Add a video to a YouTube playlist."""
    request_body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {"kind": "youtube#video", "videoId": video_id}
        }
    }
    try:
        request = youtube.playlistItems().insert(part="snippet", body=request_body)
        response = request.execute()
        print(f"✅ Added video {video_id} to playlist {playlist_id}")
    except googleapiclient.errors.HttpError as error:
        print(f"❌ Failed to add video {video_id} to playlist: {error}")


def search_youtube_video(youtube, title, artist):
    """Search for a YouTube video."""
    query = f"{title} {artist} official audio"
    try:
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=1
        )
        response = request.execute()
        items = response.get("items", [])
        if items:
            video_id = items[0]["id"]["videoId"]
            return video_id
        print(f"❌ No video found for '{title}' by '{artist}'")
    except googleapiclient.errors.HttpError as error:
        if error.resp.status == 403:
            print("❌ Quota exceeded. Retrying in 10 seconds...")
            time.sleep(10)  # Wait for 10 seconds before retrying
            return search_youtube_video(youtube, title, artist)  # Retry the search
        print(f"❌ Error searching for '{title}' by '{artist}': {error}")
    return None


def process_shazam_csv(csv_file):
    """Read Shazam CSV and return a list of (title, artist) tuples."""
    try:
        df = pd.read_csv(csv_file, header=1)  # Skip header row
        songs = [(row["Title"], row["Artist"]) for _, row in df.iterrows() if pd.notna(row["Title"])]
        print(f"✅ Loaded {len(songs)} songs from Shazam CSV")
        return songs
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return []


def main():
    """Main function to process Shazam CSV and update a YouTube playlist."""
    youtube = authenticate_youtube()
    if not check_youtube_channel(youtube):
        print("Exiting program. Please ensure your YouTube account has an active channel.")
        return

    csv_file = "shazamlibrary.csv"  # Update file path if needed
    playlist_title = "My Shazam Playlist"  # Title of the existing playlist
    playlist_description = "Songs imported from my Shazam library."

    songs = process_shazam_csv(csv_file)
    if not songs:
        print("No songs to process. Exiting.")
        return

    # Try to get the existing playlist by title
    playlist_id = get_existing_playlist(youtube, playlist_title)

    if not playlist_id:
        print("❌ No existing playlist found. Exiting.")
        return

    # Get the existing videos in the playlist
    existing_videos = get_playlist_videos(youtube, playlist_id)

    for title, artist in songs:
        # Check if the song is already in the playlist (case-insensitive)
        song_title_lower = title.lower()
        if any(song_title_lower in existing_video for existing_video in existing_videos):
            print(f"🔁 Skipping song already in playlist: {title} by {artist}")
            continue

        video_id = search_youtube_video(youtube, title, artist)
        if video_id:
            add_video_to_playlist(youtube, playlist_id, video_id)


if __name__ == "__main__":
    main()

import os
import json
import pandas as pd
import time
import requests
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

# Values from your cURL command
EDIT_PLAYLIST_URL = "https://www.youtube.com/youtubei/v1/browse/edit_playlist?prettyPrint=false"
HEADERS = {
    "authorization": "SAPISIDHASH 1743392978_3c811564245960ea345d38a82544d6af4335ad1f_u SAPISID1PHASH 1743392978_3c811564245960ea345d38a82544d6af4335ad1f_u SAPISID3PHASH 1743392978_3c811564245960ea345d38a82544d6af4335ad1f_u",
    "content-type": "application/json",
    # Optional: Add cookie if needed (test without first)
    "cookie": "VISITOR_INFO1_LIVE=XFfeb6ILfMc; VISITOR_PRIVACY_METADATA=CgJNQRIEGgAgFA%3D%3D; VISITOR_INFO1_LIVE=OjuAtj7Oh0o; VISITOR_PRIVACY_METADATA=CgJNQRIEGgAgEA%3D%3D; HSID=AZBqBfKYTuHeObVxM; SSID=A4qArHOBjL5nW9tEb; APISID=xjKfxOnQZXMZjC45/AUcmDLsOFcL6URyyZ; SAPISID=UTCN6dnejwnCDGCi/AE6a8XJ_OvZG4uvFc; __Secure-1PAPISID=UTCN6dnejwnCDGCi/AE6a8XJ_OvZG4uvFc; __Secure-3PAPISID=UTCN6dnejwnCDGCi/AE6a8XJ_OvZG4uvFc; SID=g.a000vQic6-sgEyLu3-QaEoxZKHW1DYhjkWN962-sb8GR2iHTiq8WLLJpivYK0ODF78t6PtGAGQACgYKAU8SARESFQHGX2MiR_2wBVNpHKZc7HZitKkwbxoVAUF8yKoBDWJlOB0ylVM4EhEJeHSs0076; __Secure-1PSID=g.a000vQic6-sgEyLu3-QaEoxZKHW1DYhjkWN962-sb8GR2iHTiq8WI2TcwIviF9GIJv5T4uSq3wACgYKAYASARESFQHGX2MiiN__QDgt6zBQFJ8OTS5tTRoVAUF8yKot7tdQYXuRv4zIod6tSj-N0076; __Secure-3PSID=g.a000vQic6-sgEyLu3-QaEoxZKHW1DYhjkWN962-sb8GR2iHTiq8W_Q_6OWbYoNjvFAt8YoK0jwACgYKAa8SARESFQHGX2MiZXIE6PiFnJAvyfLOlakRxhoVAUF8yKq2XG31e3b8ec_tuV_1U1gy0076; LOGIN_INFO=AFmmF2swRQIhAL6lARlhR8hCysXDgyqtXgw7JugdwFMAxX-oQpn4oQWdAiB7gI6JkK3_znK8OPM9i3S38yTvB2fIrzfsFKd6a9HOBQ:QUQ3MjNmeGZiSkJuT0Z4NFVUTmhtWjMxNG9ielQtb09YRTVKLTNubnZqcTlGVUNaRk82bXJ2Ql9VTndfVUFnNS1SV2wxQWFSMWdVWGVVdEd0LWloeEdSTk14WURiUnlXNDdSQWdtMTBySHU3SVdXYU5wNEREU3pRTklTb0NUNkRtakVnckdBUWpWUE9zQTM2S1NrNkl3QUYyazdvbXZ6ZERR; YSC=vjvSoYhdaCk; PREF=tz=Africa.Casablanca&f5=30000&f7=100&gl=CA&f6=40000000&f4=4000000; __Secure-ROLLOUT_TOKEN=CLTbvJXinMWspQEQiMbw98TfigMY4IHfnK-zjAM%3D; __Secure-1PSIDTS=sidts-CjIB7pHptfrEifI0mIp6kQWNXfBp0_37CWK3nHKaQJo1t7CeEdvqcsqxuN02KbdAYlQB6BAA; __Secure-3PSIDTS=sidts-CjIB7pHptfrEifI0mIp6kQWNXfBp0_37CWK3nHKaQJo1t7CeEdvqcsqxuN02KbdAYlQB6BAA; SIDCC=AKEyXzWpALfoQF3EziS05Jz2MHqYuCjzp-tZMSnikGt0dPL763Pc7nx4z7spzk6z6Wcy9h9azyo; __Secure-1PSIDCC=AKEyXzXC2WAJik_kC5ZUHbaBOYe5aow466PMRr9O3zfAI0lf0JBOsPy3SM9dMVagA0GBdaq_T-k6; __Secure-3PSIDCC=AKEyXzWLIWvHRwkqM3WJS5UHYmrjE7pY8pJSyXWM9cdBqhMFGIuccf549KMDbq_v0cMipF7lT9E; ST-1x29qd6=session_logininfo=AFmmF2swRQIhAL6lARlhR8hCysXDgyqtXgw7JugdwFMAxX-oQpn4oQWdAiB7gI6JkK3_znK8OPM9i3S38yTvB2fIrzfsFKd6a9HOBQ%3AQUQ3MjNmeGZiSkJuT0Z4NFVUTmhtWjMxNG9ielQtb09YRTVKLTNubnZqcTlGVUNaRk82bXJ2Ql9VTndfVUFnNS1SV2wxQWFSMWdVWGVVdEd0LWloeEdSTk14WURiUnlXNDdSQWdtMTBySHU3SVdXYU5wNEREU3pRTklTb0NUNkRtakVnckdBUWpWUE9zQTM2S1NrNkl3QUYyazdvbXZ6ZERR",
}

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
        return False
    except googleapiclient.errors.HttpError as error:
        if error.resp.status == 403:
            print(f"⚠️ Quota exceeded while checking channel: {error}. Assuming channel exists and continuing...")
            return True
        print(f"Error checking YouTube channel: {error}")
        return False


def get_existing_playlist(youtube, playlist_title):
    """Search for an existing YouTube playlist by title."""
    try:
        request = youtube.playlists().list(part="snippet", mine=True, maxResults=10)
        response = request.execute()
        playlists = response.get("items", [])
        for playlist in playlists:
            if playlist["snippet"]["title"].lower() == playlist_title.lower():
                print(f"✅ Found existing playlist: {playlist_title}")
                return playlist["id"]
        print(f"❌ No playlist found with the title: {playlist_title}")
    except googleapiclient.errors.HttpError as error:
        if error.resp.status == 403:
            print(f"⚠️ Quota exceeded while searching for playlist: {error}. Cannot proceed without playlist ID.")
        else:
            print(f"❌ Error searching for playlist: {error}")
    return None


def remove_playlist_duplicates(youtube, playlist_id):
    """Analyze the playlist and remove duplicate videos based on title."""
    try:
        title_to_items = {}
        next_page_token = None
        while True:
            request = youtube.playlistItems().list(part="snippet,id", playlistId=playlist_id, maxResults=50, pageToken=next_page_token)
            response = request.execute()
            for item in response.get("items", []):
                title = item["snippet"]["title"].lower()
                item_id = item["id"]
                if title in title_to_items:
                    title_to_items[title].append(item_id)
                else:
                    title_to_items[title] = [item_id]
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        duplicates_removed = 0
        for title, item_ids in title_to_items.items():
            if len(item_ids) > 1:
                for item_id in item_ids[1:]:
                    try:
                        youtube.playlistItems().delete(id=item_id).execute()
                        print(f"🗑️ Removed duplicate: '{title}' (Item ID: {item_id})")
                        duplicates_removed += 1
                    except googleapiclient.errors.HttpError as error:
                        print(f"❌ Failed to remove duplicate '{title}' (Item ID: {item_id}): {error}")
                        if error.resp.status == 403:
                            print("⚠️ Quota exceeded during duplicate removal. Continuing anyway...")
        print(f"✅ Duplicate removal complete. Removed {duplicates_removed} duplicates.")
    except googleapiclient.errors.HttpError as error:
        print(f"❌ Error analyzing playlist for duplicates: {error}")
        if error.resp.status == 403:
            print("⚠️ Quota exceeded during playlist analysis. Proceeding with rest of script...")


def get_playlist_videos(youtube, playlist_id):
    """Retrieve all video titles from a YouTube playlist."""
    existing_videos = set()
    try:
        next_page_token = None
        while True:
            request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50, pageToken=next_page_token)
            response = request.execute()
            for item in response.get("items", []):
                video_title = item["snippet"]["title"].lower()
                existing_videos.add(video_title)
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        print(f"✅ Retrieved {len(existing_videos)} videos from playlist")
    except googleapiclient.errors.HttpError as error:
        if error.resp.status == 403:
            print(f"⚠️ Quota exceeded while retrieving playlist videos: {error}. Proceeding with empty set...")
        else:
            print(f"❌ Error retrieving playlist videos: {error}")
    return existing_videos


def add_videos_to_playlist(playlist_id, video_ids):
    """Add multiple videos to a playlist using a single HTTP request (no API quota)."""
    if not video_ids:
        print("⚠️ No videos to add.")
        return

    batch_size = 50  # Practical limit based on feedback
    for i in range(0, len(video_ids), batch_size):
        batch = video_ids[i:i + batch_size]
        actions = [{"addedVideoId": video_id, "action": "ACTION_ADD_VIDEO"} for video_id in batch]
        payload = {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "CA",
                    "clientName": "WEB",
                    "clientVersion": "2.20250327.01.00"
                }
            },
            "actions": actions,
            "playlistId": playlist_id
        }

        try:
            response = requests.post(EDIT_PLAYLIST_URL, headers=HEADERS, json=payload)
            if response.status_code == 200:
                print(f"✅ Added {len(batch)} videos to playlist {playlist_id}")
            else:
                print(f"❌ Failed to add videos: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            print(f"❌ Error adding videos to playlist: {e}")


def search_youtube_video(youtube, title, artist):
    """Search for a YouTube video."""
    query = f"{title} {artist} official audio"
    try:
        request = youtube.search().list(part="snippet", q=query, type="video", maxResults=1)
        response = request.execute()
        items = response.get("items", [])
        if items:
            video_id = items[0]["id"]["videoId"]
            return video_id
        print(f"❌ No video found for '{title}' by '{artist}'")
    except googleapiclient.errors.HttpError as error:
        if error.resp.status == 403:
            print("❌ Quota exceeded. Retrying in 10 seconds...")
            time.sleep(10)
            return search_youtube_video(youtube, title, artist)
        print(f"❌ Error searching for '{title}' by '{artist}': {error}")
    return None


def process_shazam_csv(csv_file):
    """Read Shazam CSV and return a list of (title, artist) tuples."""
    try:
        df = pd.read_csv(csv_file, header=1)
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
        print("⚠️ Channel check failed. Proceeding anyway, but ensure your YouTube account has an active channel.")

    csv_file = "shazamlibrary.csv"
    playlist_title = "My Shazam Playlist"
    playlist_description = "Songs imported from my Shazam library."

    songs = process_shazam_csv(csv_file)
    if not songs:
        print("No songs to process. Exiting.")
        return

    playlist_id = get_existing_playlist(youtube, playlist_title)
    if not playlist_id:
        print("❌ No existing playlist found. Exiting.")
        return

    remove_playlist_duplicates(youtube, playlist_id)
    existing_videos = get_playlist_videos(youtube, playlist_id)

    new_video_ids = []
    for title, artist in songs:
        song_title_lower = title.lower()
        if any(song_title_lower in existing_video for existing_video in existing_videos):
            print(f"🔁 Skipping song already in playlist: {title} by {artist}")
            continue
        video_id = search_youtube_video(youtube, title, artist)
        if video_id:
            new_video_ids.append(video_id)

    add_videos_to_playlist(playlist_id, new_video_ids)


if __name__ == "__main__":
    main()

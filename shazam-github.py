import os
import json
import pandas as pd
import time
import requests
from youtubesearchpython import VideosSearch
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

TRACK_FILE = "processed_songs.json"

def load_processed_songs():
    """Load processed songs from a file."""
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            return json.load(f)
    return {"added": [], "not_found": []}

def save_processed_songs(processed_songs):
    """Save processed songs to a file."""
    with open(TRACK_FILE, "w") as f:
        json.dump(processed_songs, f, indent=4)

def main():
    """Main function to process Shazam CSV and update a YouTube playlist."""
    youtube = authenticate_youtube()

    if not check_youtube_channel(youtube):
        print("⚠️ Channel check failed. Proceeding anyway, but ensure your YouTube account has an active channel.")

    csv_file = "shazamlibrary.csv"
    playlist_title = "My Shazam Playlist"

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

    processed_songs = load_processed_songs()
    added_songs = set(processed_songs["added"])
    not_found_songs = set(processed_songs["not_found"])

    new_video_ids = []
    for title, artist in songs:
        song_identifier = f"{title} - {artist}".lower()

        if song_identifier in added_songs or any(song_identifier in vid for vid in existing_videos):
            print(f"🔁 Skipping already added song: {title} by {artist}")
            continue

        if song_identifier in not_found_songs:
            print(f"🚫 Skipping previously not found song: {title} by {artist}")
            continue

        video_id = search_youtube_video(youtube, title, artist)
        if video_id:
            new_video_ids.append(video_id)
            processed_songs["added"].append(song_identifier)
        else:
            print(f"⚠️ Could not find song: {title} by {artist}, marking for manual addition.")
            processed_songs["not_found"].append(song_identifier)

    save_processed_songs(processed_songs)
    add_videos_to_playlist(playlist_id, new_video_ids)

if __name__ == "__main__":
    main()

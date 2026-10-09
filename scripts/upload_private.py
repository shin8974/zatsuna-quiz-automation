"""Upload the generated Short as private using a stored OAuth refresh token."""
from __future__ import annotations

import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

OUT = Path("output")
EXPECTED_CHANNEL_ID = "UCZQO7v7RG7U8niQ5287osDQ"


def main():
    metadata = (OUT / "metadata.txt").read_text(encoding="utf-8").splitlines()
    title = metadata[0]
    description = "\n".join(metadata[2:])
    credentials = Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly",
        ],
    )
    youtube = build("youtube", "v3", credentials=credentials)
    channel = youtube.channels().list(part="id", mine=True).execute()["items"][0]
    if channel["id"] != EXPECTED_CHANNEL_ID:
        raise RuntimeError("OAuth token is not connected to the ざつなクイズ channel.")
    result = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": description, "categoryId": "27"},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False},
        },
        media_body=MediaFileUpload(str(OUT / "final.mp4"), mimetype="video/mp4", resumable=True),
    ).execute()
    print(json.dumps({"video_id": result["id"], "privacy": "private"}))


if __name__ == "__main__":
    main()


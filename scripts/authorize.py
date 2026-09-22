"""One-time local OAuth authorization for the GitHub Actions uploader.

Run this only on the user's PC.  The browser consent screen returns a refresh
token, which the user then saves in GitHub Secrets.  Never commit the client
JSON or the printed token.
"""
from __future__ import annotations

import argparse

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("client_json", help="Downloaded OAuth desktop-client JSON")
    args = parser.parse_args()
    flow = InstalledAppFlow.from_client_secrets_file(args.client_json, SCOPE)
    credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    if not credentials.refresh_token:
        raise RuntimeError("Refresh token was not returned. Revoke the app grant and retry.")
    print("\nSave this ONLY as the GitHub secret YT_REFRESH_TOKEN:\n")
    print(credentials.refresh_token)


if __name__ == "__main__":
    main()


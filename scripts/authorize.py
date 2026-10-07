"""One-time local OAuth authorization for the GitHub Actions uploader.

Run this only on the user's PC.  The browser consent screen returns a refresh
token, which the user then saves in GitHub Secrets.  Never commit the client
JSON or the printed token.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("client_json", help="Downloaded OAuth desktop-client JSON")
    parser.add_argument("--token-file", default="token.json", help="Local ignored token output")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the consent URL instead of relying on the system browser.",
    )
    args = parser.parse_args()
    flow = InstalledAppFlow.from_client_secrets_file(args.client_json, SCOPE)
    credentials = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
        open_browser=not args.no_browser,
    )
    if not credentials.refresh_token:
        raise RuntimeError("Refresh token was not returned. Revoke the app grant and retry.")
    Path(args.token_file).write_text(credentials.to_json(), encoding="utf-8")
    print("Authorization complete. The refresh token was saved locally in the ignored token file.")


if __name__ == "__main__":
    main()


import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://www.googleapis.com/youtube/v3/"
CHANNEL_HANDLE = "@hitgs_offcl"
OUTPUT_FILE = Path("videos.js")


def youtube_api(endpoint, **params):
    params["key"] = os.environ["YOUTUBE_API_KEY"]

    url = API_URL + endpoint + "?" + urllib.parse.urlencode(params)

    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def main():
    if not os.environ.get("YOUTUBE_API_KEY"):
        raise SystemExit("YOUTUBE_API_KEY is missing")

    channel_data = youtube_api(
        "channels",
        part="snippet,contentDetails",
        forHandle=CHANNEL_HANDLE
    )

    channels = channel_data.get("items", [])

    if len(channels) != 1:
        raise SystemExit("Official channel not found")

    channel = channels[0]
    channel_name = channel["snippet"]["title"]

    uploads_playlist = channel["contentDetails"][
        "relatedPlaylists"
    ]["uploads"]

    official_videos = []
    page_token = None

    while True:
        params = {
            "part": "snippet",
            "playlistId": uploads_playlist,
            "maxResults": 50
        }

        if page_token:
            params["pageToken"] = page_token

        response = youtube_api("playlistItems", **params)

        for item in response.get("items", []):
            snippet = item.get("snippet", {})

            video_id = snippet.get(
                "resourceId", {}
            ).get("videoId")

            title = snippet.get("title", "")
            date = snippet.get("publishedAt", "")[:10]

            if not video_id or not re.fullmatch(
                r"[A-Za-z0-9_-]{11}", video_id
            ):
                continue

            if title in ("Private video", "Deleted video"):
                continue

            if not date:
                continue

            official_videos.append({
                "title": title,
                "url": (
                    "https://www.youtube.com/watch?v="
                    + video_id
                ),
                "year": date[:4],
                "category": "OFFICIAL",
                "member": "ALL",
                "channel": channel_name,
                "date": date
            })

        page_token = response.get("nextPageToken")

        if not page_token:
            break

    # 기존에 수동 등록한 다른 카테고리 영상 유지
    existing_videos = []

    if OUTPUT_FILE.exists():
        old_content = OUTPUT_FILE.read_text(
            encoding="utf-8"
        )

        match = re.search(
            r"const\s+videos\s*=\s*(\[.*?\])\s*;",
            old_content,
            re.S
        )

        if not match:
            raise SystemExit(
                "Cannot parse existing videos.js"
            )

        try:
            existing_videos = json.loads(match.group(1))
        except json.JSONDecodeError:
            print("Existing videos.js is not valid JSON; skipping legacy entries.")
            existing_videos = []

    other_videos = [
        video for video in existing_videos
        if isinstance(video, dict)
        and str(
            video.get("category", "")
        ).upper() != "OFFICIAL"
        and video.get("url") != (
            "https://www.youtube.com/watch?v=VIDEO_ID"
        )
    ]

    # URL 기준 중복 제거
    unique_videos = {}

    for video in official_videos + other_videos:
        url = video.get("url")

        if url and url not in unique_videos:
            unique_videos[url] = video

    # 최신순 정렬
    sorted_videos = sorted(
        unique_videos.values(),
        key=lambda video: video.get("date", ""),
        reverse=True
    )

    new_content = (
        "const videos = "
        + json.dumps(
            sorted_videos,
            ensure_ascii=False,
            indent=2
        )
        + ";\n"
    )

    OUTPUT_FILE.write_text(
        new_content,
        encoding="utf-8"
    )

    print(
        f"Official videos: {len(official_videos)}"
    )
    print(
        f"Total archive videos: {len(sorted_videos)}"
    )


if __name__ == "__main__":
    main()

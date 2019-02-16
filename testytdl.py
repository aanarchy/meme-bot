import youtube_dl

opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': '%(id)s.%(ext)s',
    'quiet': True,
}

youtube = youtube_dl.YoutubeDL(opts)


def from_youtube(request):
    """Gets video info."""
    query = "ytsearch:" + str(request)
    if request.startswith("https://"):
        info = youtube.extract_info(request, download=False)
    else:
        info = youtube.extract_info(query, download=False)
        entries = info.get("entries", None)
        extracted_info = entries[0]
        print(extracted_info)


request = input()
from_youtube(request)
